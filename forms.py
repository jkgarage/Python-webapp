from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, RadioField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed


class ContactForm(Form):
  name = TextField('Name:', validators=[validators.required()])
  email = TextField('Email:', validators=[validators.required(), 
  	validators.Length(min=6, max=35)])
  comment = TextAreaField('Your Message:', validators=[validators.required() ])


class ParagraphForm(Form):
  # TODO(jk): impose a length limit
  paragraph = TextAreaField('Paragraph:', validators=[validators.required() ])


class PhotoForm(FlaskForm):
  photo = FileField(validators=[FileRequired(),
  	FileAllowed(['jpg', 'png', 'bmp', 'svg', 'jpeg'],
  		'Please upload images only (.jpg, .jpeg, .png, .bmp, .svg).')
  	])


class CarPlateForm(Form):
  number = TextField('Number:', validators=[validators.required(),
  	validators.Length(min=2, max=15, message='Make sure your plate number is 2-15 chars.')])

  fg_color = RadioField('Text color',
  	choices=[('black','Black'), ('white','White')], 
  	validators=[validators.required()])
  
  bg_color = RadioField('Plate color',
  	choices=[('blue','Blue'), ('black','Black'), ('red','Red'),
  	         ('yellow','Yellow'), ('white','White')],
  	validators=[validators.required()])