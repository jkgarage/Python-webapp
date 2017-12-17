# This Python file uses the following encoding: utf-8
from google.appengine.api import memcache
import json, re, sys

carplate_color_mapping = {}
carplate_mapping = {}

CARPLATE_FILE_PATH = 'data/carplate.csv'
CARPLATE_COLOR_FILE_PATH = 'data/carplatecolor.csv'

def load_carplate_number_mapping():
  """Load the list of carplates number-origin of issuance into a dict.

  Path to the data file is set in CARPLATE_FILE_PATH.
  Data file is in csv format, comma separated with 3 columns: Country,Số,
  Tỉnh/thành phố/Don vi. Example: VN,12,Lạng Sơn

  Returns:
    A dict containing mapping of carplate and issuance origin.
      Key of an element is the 2 digit prefix of carplate.
      Value of an elements is the issuance origin.
  """
  f = open(CARPLATE_FILE_PATH, 'r')
  if f: header = f.readline()
  carplate_list = {}
  for line in f:
    line = line.decode('utf-8')
    line_data = line.rstrip().split(',')
    carplate_list[line_data[1].upper()] = line_data[2]
  return carplate_list


def load_carplate_color_mapping():
  """Load the list of carplate color-type of vehicle into a dict.

  Path to the data file is set in CARPLATE_COLOR_FILE_PATH.
  Data file is in csv format, comma separated with 5 columns: 
  Country,Fg color,Bg color,Vehicle type,Code.
  Color code is in English, and lower case.
  Example: VN,black,white,Personal and Business vehicle,personal

  Returns:
    A dict containing mapping of carplate color and vehicle type.
      Key of an element is a tuple (fg color, bg color).
      Value of an elements is a tuple (Veh type description, Veh type code).
  """
  f = open(CARPLATE_COLOR_FILE_PATH, 'r')
  if f: header = f.readline()
  carplate_list = {}
  for line in f:
    line = line.decode('utf-8')
    line_data = line.rstrip().split(',')
    carplate_list[(line_data[1], line_data[2])] = (line_data[3], line_data[4])
  return carplate_list


if memcache.get('CARPLATE_MAPPING'):
  carplate_mapping = memcache.get('CARPLATE_MAPPING')
else:
  carplate_mapping = load_carplate_number_mapping()
  memcache.set('CARPLATE_MAPPING', carplate_mapping)

if memcache.get('CAPLATE_COLOR_MAPPING'):
  carplate_color_mapping = memcache.get('CAPLATE_COLOR_MAPPING')
else:
  carplate_color_mapping = load_carplate_color_mapping()
  memcache.set('CAPLATE_COLOR_MAPPING', carplate_color_mapping)


def get_location(number):
  default_message = 'No location found'
  return carplate_mapping.get(number[:2].upper(), default_message)


def get_vehicle_type(color):
  """
  Args:
    color: a tuple of (fg color, bg color)
  Returns:
    A tuple (vehicle type description, vehicle type code)
  """
  default_message = ('Undefined type', 'undefined')
  return carplate_color_mapping.get(color, default_message)

