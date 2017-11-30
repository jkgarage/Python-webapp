"""This is the main app that host all works by JingkeeGarage.

This web app runs on Flask framework. 
"""
from flask import Flask, render_template, flash, request
from operator import itemgetter
from nltk.corpus import stopwords
from forms import ParagraphForm, PhotoForm, ContactForm, CarPlateForm
from werkzeug.utils import secure_filename
import os, re, json, uuid

import controls
import CarPlate

# App config.
DEBUG = True

app = Flask(__name__)
app.config.from_object('config')

UPLOAD_PATH = app.config['UPLOAD_PATH']

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = PhotoForm()

    if form.validate_on_submit():
        f = form.photo.data
        filename = str(uuid.uuid1()) + '_' + secure_filename(f.filename)
        print ( 'filename:: %s' % filename )
        print ( 'path:: %s' % os.path.join(
            UPLOAD_PATH, filename
        ) )

        f.save(os.path.join(
            UPLOAD_PATH, filename
        ))
        #return redirect(url_for('upload'))
        flash("Image uploaded successfully !")
        return render_template('upload.html', form=form)

    error = None
    if 'photo' in form.errors: error = form.errors['photo']
    return render_template('upload.html', form=form, error=error)


@app.route("/hskaid", methods=['GET', 'POST'])
def hskaid():
    form = ParagraphForm(request.form)
    error = None
    processed_text = None
    result_json = None

    print form.errors
    if request.method == 'POST':
        paragraph=request.form['paragraph']  #paragraph is already in utf-8 format

        if form.validate():
            flash(paragraph)
            processed_text = controls.format_text_per_hsk(paragraph)
        else:
            flash('Error: Failed xap mat. All the form fields are required. ')
            error = 'Error'
    
    return render_template('hskaid.html', form=form, error=error, 
        hsk_format=app.config['FORMAT_PER_HSK_LEVEL'], processed_text=processed_text,
        result_json=controls.jsonify_hsk_statistics())


@app.route("/", methods=['GET', 'POST'])
def processtext():
    form = ParagraphForm(request.form)
    error = None
    result_table = None
 
    if request.method == 'POST':
        paragraph=request.form['paragraph']  #paragraph is already in utf-8 format
        
        if form.validate():
            sorted_words = controls.word_processing(paragraph)
            flash(paragraph)
            result_table = controls.convert_data_to_html_table(sorted_words,
                'result_table', 'table table-striped')
        else:
            flash('Error: Failed xap mat. All the form fields are required. ')
            error = 'Error'
    
    return render_template('processtext_form.html', form=form, 
        error=error, result_table=result_table)


@app.route("/platecheck", methods=['GET', 'POST'])
def platecheck():
    form = CarPlateForm(request.form)
    plate = None
    payload = None

    if request.method == 'POST':
        number=request.form['number']
        fg_color=request.form['fg_color']
        bg_color=request.form['bg_color']

        str = number + '-' + fg_color + '-' + bg_color
        print str

        if form.validate():
            location = CarPlate.get_location(number)
            vehicle_type = CarPlate.get_vehicle_type((fg_color, bg_color))
            message = ('Plate:[%s, %s on %s] is a %s issued in %s.'
                % (number, fg_color, bg_color, vehicle_type[0], location))
            payload = {'bg_color':bg_color, 'fg_color': fg_color, 
              'number': number, 'vehicle_type': vehicle_type,
              'location':location}
            flash(message)
        else:
            flash('Error: %s' % form.errors)
 
    return render_template('platecheck.html', form=form, carplate=payload)


@app.route("/contact", methods=['GET', 'POST'])
def contactme():
    form = ContactForm(request.form)
 
    if request.method == 'POST':
        name=request.form['name']
        comment=request.form['comment']
        email=request.form['email']
        print name, " ", email, " ", comment
 
        if form.validate():
            flash('Thanks for contacting me, ' + name)
        else:
            flash('Error: ' + form.errors)
 
    return render_template('contactme.html', form=form)


if __name__ == "__main__":
    app.run()