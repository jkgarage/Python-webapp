# This file is in encoding: utf-8
"""This is the main app that host all works by JingkeeGarage.

This web app runs on Flask framework. 
"""
from flask import Flask, render_template, flash, request
from forms import ParagraphForm, PhotoForm, ContactForm, CarPlateForm
from werkzeug.utils import secure_filename
import logging, traceback

import os, re, json, uuid
from random import *

import controls
import CarPlate

from models import HskText
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import memcache

# App config.
DEBUG = True

app = Flask(__name__)
app.config.from_object('config')

UPLOAD_PATH = app.config['UPLOAD_PATH']

logging.basicConfig(filename='app.log', level=logging.DEBUG)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = PhotoForm()

    if form.validate_on_submit():
        f = form.photo.data
        filename = str(uuid.uuid1()) + '_' + secure_filename(f.filename)
        logging.debug('filename:: %s' % filename)
        logging.debug('path:: %s' % os.path.join(
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


@app.route("/hsk-nodb", methods=['GET', 'POST'])
def hsk_nodb():
    form = ParagraphForm(request.form)
    error = None
    processed_text = None
    hsk_stat_list = []

    if request.method == 'POST':
        paragraph=request.form['paragraph']  #paragraph is already in utf-8 format

        if form.validate():
            flash(paragraph)
            processed_text = controls.format_text_per_hsk(paragraph)
            hsk_stat_list = controls.hsk_statistics()
        else:
            flash('Error: Failed xap mat. All the form fields are required. ')
            error = 'Error'
            logging.error(form.errors)
    
    return render_template( 'hskaid.html', form=form, error=error, 
        hsk_format=app.config['FORMAT_PER_HSK_LEVEL'], 
        processed_text=processed_text,
        result_json=json.dumps(hsk_stat_list) )


@app.route("/zhvocab", methods=['GET', 'POST'])
def zhvocab_assist():
    articles = None
    try:
        articles = controls.get_text_last_hours(24)
    except Exception as e:
        logging.error(traceback.format_exc())

    form = ParagraphForm(request.form)
    error = None
    processed_text = None
    hsk_stat_list = []

    if request.method == 'POST':
        paragraph=request.form['paragraph']  #paragraph is already in utf-8 format

        if form.validate():
            try:
                flash(paragraph)
                processed_text = controls.format_text_per_hsk(paragraph)
                hsk_stat_list = controls.hsk_statistics()
                processed_breakdown = controls.get_hsk_breakdown()

                #save to datastore
                hskpc = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                for item in hsk_stat_list:
                    if item[0] == 'HSK-1': 
                        hskpc[0] = item[1]
                    elif item[0] == 'HSK-2': 
                        hskpc[1] = item[1]
                    elif item[0] == 'HSK-3': 
                        hskpc[2] = item[1]
                    elif item[0] == 'HSK-4':
                        hskpc[3] = item[1]
                    elif item[0] == 'HSK-5':
                        hskpc[4] = item[1]
                    elif item[0] == 'HSK-6':
                        hskpc[5] = item[1]

                total = int(sum(hskpc))
                if total > 0 : hskpc = [v*1.0/total for v in hskpc]

                logging.debug ('Client address %s' % request.remote_addr)

                ent = HskText(u_content=paragraph,
                    u_annotation=json.dumps(processed_breakdown),
                    totalhskcount = total,
                    hsk1percentage = hskpc[0],
                    hsk2percentage = hskpc[1],
                    hsk3percentage = hskpc[2],
                    hsk4percentage = hskpc[3],
                    hsk5percentage = hskpc[4],
                    hsk6percentage = hskpc[5],
                    address = ('%s' % request.remote_addr) )
                
                ent_key = ent.put()
                logging.debug( '<<< Successful >>> %s saved.' % ent_key )
            except Exception as e:
                logging.error(traceback.format_exc())
        else:
            flash('Error: Failed xap mat. All the form fields are required. ')
            error = 'Error'
            logging.error(form.errors)
    
    return render_template('zhvocab_assist.html', form=form, error=error, 
        hsk_format=app.config['FORMAT_PER_HSK_LEVEL'], 
        processed_text=processed_text,
        result_json=json.dumps(hsk_stat_list), articles = articles)


@app.route("/article/<int:article_id>")
def show_article(article_id):
    article = None
    try:
        article = controls.get_text_by_id(article_id)
        logging.info('Id=%s' % article_id)
    except Exception as e:
        logging.error(traceback.format_exc())

    if not article:
        logging.error('Aborting........................')
        abort()
    else:
        try:
            annotation = json.loads(article.u_annotation)
            processed_text = controls.format_text_per_breakdown(annotation)
        except Exception as e:
            logging.error(traceback.format_exc())
        return render_template('zhvocab_assist_article.html', 
        hsk_format=app.config['FORMAT_PER_HSK_LEVEL'], 
        processed_text=processed_text,
        result_json = None )


@app.route("/", methods=['GET', 'POST'])
def processtext():
    form = ParagraphForm(request.form)
    error = None
    result_table = None
    result_statistic = None
 
    if request.method == 'POST':
        paragraph=request.form['paragraph']  #paragraph is already in utf-8 format
        
        if form.validate():
            sorted_words = controls.word_processing(paragraph)
            result_statistic = {'characters':len(paragraph), 
                'words':controls.count_words(paragraph)}
            flash(paragraph)
            result_table = controls.convert_data_to_html_table(sorted_words,
                'result_table', 'table table-striped')
        else:
            flash('Error: Failed xap mat. All the form fields are required. ')
            error = 'Error'
            logging.error(form.errors)
    
    return render_template('processtext_form.html', form=form, 
        error=error, result_table=result_table, result_statistic=result_statistic)


@app.route("/platecheck", methods=['GET', 'POST'])
def platecheck():
    form = CarPlateForm(request.form)
    plate = None
    payload = None

    if request.method == 'POST':
        number=request.form['number']
        fg_color=request.form['fg_color']
        bg_color=request.form['bg_color']

        logging.debug('%s-%s-%s' % (number, fg_color, bg_color))

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
            logging.error('Error: %s' % form.errors)
 
    return render_template('platecheck.html', form=form, carplate=payload)


@app.route("/contact", methods=['GET', 'POST'])
def contactme():
    form = ContactForm(request.form)
 
    if request.method == 'POST':
        name=request.form['name']
        comment=request.form['comment']
        email=request.form['email']
        logging.debug('%s %s %s' % (name, email, comment))
 
        if form.validate():
            try:
                flash('Thanks for contacting me, %s !' % name)
                sender_address = app.config['EMAIL_ADDRESS_FROM']

                mail.send_mail(sender=sender_address,
                       to=app.config['CONTACT_ME_SEND_TO'],
                       subject=('[jkgarage-home] Message from %s<%s>' % (name, email)),
                       body=comment)
            except Exception as e:
                print (traceback.format_exc())
                logging.error(traceback.format_exc())

        else:
            flash('Error: %s' % form.errors)
            logging.error('Error: %s' % form.errors)
 
    return render_template('contactme.html', form=form)


if __name__ == "__main__":
    app.run()