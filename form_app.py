"""This is a webapp to analyse word frequency of a given paragraph.

This web app runs on Flask framework. The program displays a web form
to enable user to input any paragraph. It then presents a table of
words and frequency found in the input paragraph.
"""
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from operator import itemgetter
from nltk.corpus import stopwords
import re

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'my_secret_key_betyoudontknow'
 
class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required(), 
        validators.Length(min=6, max=35)])
    password = TextField('Password:', validators=[validators.required(), 
        validators.Length(min=3, max=35)])
 
class NameForm(Form):
    name = TextAreaField('Name:', validators=[validators.required()])

class ParagraphForm(Form):
    paragraph = TextAreaField('Paragraph:', validators=[validators.required() ])


@app.route("/processtext", methods=['GET', 'POST'])
def processtext():
    form = ParagraphForm(request.form)
    error = None
    result_table = None
 
    print form.errors
    if request.method == 'POST':
        paragraph=request.form['paragraph']  #paragraph is already in utf-8 format

        if form.validate():
            sorted_words = word_processing(paragraph)
            flash(paragraph)
            result_table = convert_data_to_html_table(sorted_words,
                'result_table', 'table table-striped')
        else:
            flash('Error: Failed xap mat. All the form fields are required. ')
            error = 'Error'
    
    return render_template('processtext_form.html', form=form, 
        error=error, result_table=result_table)


@app.route("/aloha", methods=['GET', 'POST'])
def hello():
    form = NameForm(request.form)
 
    print form.errors
    if request.method == 'POST':
        name=request.form['name']
        print name
 
        if form.validate():
            # Save the comment here.
            flash('Hello ' + name)
        else:
            flash('Error: Failed xap mat. All the form fields are required. ')
 
    return render_template('hello_form_bootstrap.html', form=form)

 
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = ReusableForm(request.form)
 
    print form.errors
    if request.method == 'POST':
        name=request.form['name']
        password=request.form['password']
        email=request.form['email']
        print name, " ", email, " ", password
 
        if form.validate():
            # Save the comment here.
            flash('Thanks for registration ' + name)
        else:
            flash('Error: All the form fields are required. ')
 
    return render_template('signup_form_bootstrap.html', form=form)


##############################################################################
## The following sections are functions to process data - brain of the program
##############################################################################
def word_processing(text):
    """Processes input text to count frequency of its words.

    English stop words are ignored from the text and will not be counted in result.
    Words of different capitalization are treated differently. Example:
    "the" and "The" are counted respectively.

    Args:
        text: the text must be in utf-8 encode. It may contain both Roman 
            characters and Chinese, Japanese, Korean characters. Example:
            'I have a dream have have a dream.'

    Returns:
        A list of words and their frequency in the input text. Example:
        [('I', 1), ('have', 3), ('dream', 2)]
    """
    word_frequency = {}
    stop_words = stopwords.words('english')

    # Step1. extract all CJK words first
    pattern = re.compile(ur'[\u4e00-\ufaff]')
    all_cjk = pattern.findall(text)
    roman_only_text = pattern.sub('', text)

    # Step2. continue to analyse the roman words
    #re.split('\W+', text) doesn't work for unicode text (eg. Vietnamese)
    words = re.split('[ .,/?:;!"&*()\[\]\-]', roman_only_text)
    words += all_cjk
    for word in words:
        if word not in word_frequency:
            word_frequency[word] = 1
        else:
            word_frequency[word] += 1
    sorted_words = sorted(word_frequency.items(),key=itemgetter(1),
        reverse=True)

    #remove the English stop words
    iterator = sorted_words[:]
    for item in iterator:
        if item[0] == ' ' or item[0] == '':
            sorted_words.remove(item)
        else:
            for word in stop_words:
                if item[0] == word:
                    sorted_words.remove(item)
                    break

    return sorted_words


def convert_data_to_html_table(word_frequency, id_name, class_name):
    """Converts list of words and frequency to html table format.

    The html table will be passed onto template for rendering. The table id 
    and class are required for table to be rendered in proper format.

    Args:
        word_frequency: list of words and their frequency. Example:
                      [('I', 1), ('have', 3), ('dream', 2)]
        id_name: id of the html table. This should be a unique id across all
               elements in the template html page. This id must match with
               that of the DataTable on template page.
        class_name: class of the html table. This decides format of the table. 

    Returns:
        A string representing an HTML table, its id and its class are assigned
        from id_name, class_name.
    """
    str_result = ''
    str_result += '<table id="' + id_name + '" class="' + class_name + '">'
    str_result += '<thead><tr><th>Word</th><th>Frequency</th></tr></thead>'
    for item in word_frequency:
        str_result += '<tr><td>%s</td><td>%d</td></tr>' % (item[0], item[1])
    str_result += '</table>'
    
    return str_result


def is_text_cjk (text):
    """Checks whether a text mostly consists of Roman characters or CJK.

    Args:
        text: the input text, may contain both Roman characters and CJK.

    Returns:
        True if > 50% of text is CJK characters; False otherwise.
    """
    pattern = re.compile(ur'[\u4e00-\ufaff]')
    all_cjk = pattern.findall(text)
    return len(all_cjk)*1.0 / len(text) > 0.5


if __name__ == "__main__":
    app.run()