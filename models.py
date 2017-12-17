from google.appengine.ext import ndb

class HskText(ndb.Model):
  """Models a Chinese text entry with HSK annotation.

  u_content : content must be already encoded in utf-8
  """
  u_content = ndb.TextProperty()
  u_annotation = ndb.TextProperty()
  totalhskcount = ndb.IntegerProperty()
  hsk1percentage = ndb.FloatProperty()
  hsk2percentage = ndb.FloatProperty()
  hsk3percentage = ndb.FloatProperty()
  hsk4percentage = ndb.FloatProperty()
  hsk5percentage = ndb.FloatProperty()
  hsk6percentage = ndb.FloatProperty()
  address = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)

