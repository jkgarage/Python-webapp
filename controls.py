# This Python file uses the following encoding: utf-8
from operator import itemgetter
import json, re, sys, logging
import config
from google.appengine.api import memcache
from google.appengine.ext import ndb
from datetime import datetime, timedelta
from models import HskText

logging.basicConfig(filename='app.log', level=logging.DEBUG)

hsk_breakdown = []

def load_HSK_vocabulary():
    """Load the list of HSK vocabulary of all levels into a dict.

    Path to the data file for all HSK vocabulary is set using global var
    HSK_FILE_PATH.
    Data file is in csv format, comma separated with 3 columns: hsk level, 
    Chinese word, hanyu pinyin.

    Returns:
        A dict containing all vocabulary of all HSK levels.
          Key of an element is the Chinese word.
          Value of an elements is a tuple of 2 values: (1) HSK level, 
          and (2) hanyu pinyin.
    """
    f = open(config.HSK_FILE_PATH, 'r')
    if f: header = f.readline()
    hsk_list = {}
    for line in f:
    	line = line.decode('utf-8')
        line_data = line.rstrip().split(',')
        hsk_list[line_data[1]] = (line_data[0], line_data[2])
    return hsk_list


if memcache.get('HSK_VOCABULARY'):
    HSK_VOCABULARY = memcache.get('HSK_VOCABULARY')
else:
    HSK_VOCABULARY = load_HSK_vocabulary()
    memcache.set('HSK_VOCABULARY', HSK_VOCABULARY)


def analyse_sentence_into_hsk(utf8_sentence):
    """Analyses a Chinese sentence, categorises its words into HSK buckets.

    Args: 
        utf8_sentence: Chinese text, in utf-8 encoding.

    Returns:
        A list of tuples consisting of (1) the word, (2) HSK level, and (3)
          hanyu pinyin.
          If the word does not belong in HSK vocabulary, HSK level and hanyu
          pinyin are both captured as None.
          Example: [('还','3','huán'), ('终',None,None), ('谷歌','name','gǔ gē')]
    """
    result = []
    pattern = re.compile(ur'[\u4e00-\ufaff]|[^\u4e00-\ufaff]+')
    all_cjk = pattern.findall(utf8_sentence)
    stop = False

    while not stop:
        word_len = min(config.HSK_MAX_LENG, len(all_cjk))
        word = ''

        while word_len > 0:
            word = ''.join(all_cjk[:word_len])
            if word in HSK_VOCABULARY:
                result.append((word, HSK_VOCABULARY[word][0], HSK_VOCABULARY[word][1]))
                #remove this matched word from the sentence
                for i in range(0,word_len):
                    del all_cjk[0]
                break
            else:
                word_len -= 1

        if word_len == 0:
            result.append((word, None, None))
            if len(all_cjk) > 0: del all_cjk[0]

        if len(all_cjk) == 0: stop = True

    return result


def html_format_per_hsk(hsk_word_tuple):
    """Format the display into HTML tags based on hsk level of the word.

    The HTML display includes (1) highlighting word, and (2) tooltip showing
    hanyu pinyin.

    Args:
        hsk_word_tuple: a tuple of (1) Chinese word, (2) its HSK level, 
          and (3) hanyu pinyin. The text encoding is in utf-8.
          Example: ('少', '1', 'shǎo').

    Returns:
        A string representing HTML code to display the Chinese word accordingly
          to its HSK level.
    """
    hsk_level = hsk_word_tuple[1]
    if hsk_level is None:
        pattern = re.compile('\r+\n+')
        str = pattern.sub('<br />', hsk_word_tuple[0])
        return str
    else:
        tooltip_str = 'data-toggle="tooltip" title="' + hsk_word_tuple[2] + '"'
        return ('<span class="' + config.FORMAT_PER_HSK_LEVEL[hsk_level] + '" '
            + tooltip_str + '>' + hsk_word_tuple[0] + '</span>')


def format_text_per_hsk(utf8_text):
    """Format display of a text into HTML tags based on hsk level of the words.

    The HTML display includes (1) highlighting word, and (2) tooltip showing
    hanyu pinyin.

    Args:
        utf8_text: a piece of Chinese text. The text encoding is in utf-8.

    Returns:
        A string representing HTML code to display the Chinese text accordingly
          to HSK levels.
    """
    global hsk_breakdown
    hsk_breakdown = analyse_sentence_into_hsk(utf8_text)
    result_text = ''

    for item in hsk_breakdown:
        result_text += html_format_per_hsk(item)
    return result_text


def format_text_per_breakdown(hsk_breakdown):
    result_text = ''
    for item in hsk_breakdown:
        result_text += html_format_per_hsk(item)
    return result_text


def get_hsk_breakdown():
    global hsk_breakdown
    return hsk_breakdown

#TODO(jk): I am lazy here. Should package the whole class into an Object.
def hsk_statistics():
    """Return JSON object that captures the statistics of HSK words in text.

    To return meaningful result, this function should be called after
    format_text_per_hsk() has been called.

    Args:
        Implicit variable: global variable hsk_breakdown should have been
          computed. This is a list of tuples (word, hsk_level, hanyu_pinyin).

    Returns:
        #A JSON object capturing number of words found in text per HSK level.
        A list of 2-element array: each 2-element array [HSK-x, count of words]
    """
    if hsk_breakdown is None or not hsk_breakdown:
        return []

    statistics_dict = {}
    for item in hsk_breakdown:
        if item[1] is not None:
            statistics_dict[item[1]] = statistics_dict.get(item[1], 0) + 1

    statistics_list = [[k, v] for k,v in statistics_dict.items()]

    #update the numeric HSK level to be more descriptive (eg. '1' -> 'HSK-1')
    mapping = ({'1':'HSK-1', '2':'HSK-2', '3':'HSK-3', '4':'HSK-4', '5':'HSK-5',
        '6':'HSK-6'})
    return [ [mapping.get(a,'Non-HSK'), b] for a,b in statistics_list ]


def get_text_last_hours(number_of_hours):
    last_x_hr = timedelta(hours=number_of_hours)
    timestamp_xhrs_ago = datetime.now() - last_x_hr
    query = HskText.query(HskText.date >= timestamp_xhrs_ago)
    return query.fetch(30)


def get_text_by_id(id):
    return HskText.get_by_id(id)

    
##############################################################################
## The following sections are functions to process word frequency
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
    stop_words = config.ENGLISH_STOPWORDS

    # Step1. extract all CJK words first
    pattern = re.compile(ur'[\u4e00-\ufaff]')
    all_cjk = pattern.findall(text)
    roman_only_text = pattern.sub('', text)

    pattern = re.compile('\r+\n+')
    roman_only_text = pattern.sub('. ', roman_only_text)

    # Step2. continue to analyse the roman words
    #re.split('\W+', text) doesn't work for unicode text (eg. Vietnamese)
    words = re.split('[ .,/?:;!"&*()\[\]\-]+', roman_only_text)
    words += all_cjk
    for word in words:
        if word == '': continue
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


def count_words(text):
    """Processes input text to count number of words.

    English stop words are counted in result.

    Args:
        text: the text must be in utf-8 encode. It may contain both Roman 
            characters and Chinese, Japanese, Korean characters. Example:
            'I have a dream have have a dream.'

    Returns:
        An integer indicating the number of words in text.
    """
    # Step1. extract all CJK words first
    pattern = re.compile(ur'[\u4e00-\ufaff]')
    all_cjk = pattern.findall(text)
    roman_only_text = pattern.sub('', text)

    pattern = re.compile('\r+\n+')
    roman_only_text = pattern.sub('. ', roman_only_text)
    logging.info('roman_only_text: %s' % roman_only_text)

    words = re.split('[ .,/?:;!"&*()\[\]\-]+', roman_only_text)
    logging.info('words - before cjk: %s' % words)
    words += all_cjk
    words = [v for v in words if v != '']
    logging.info('words - after cjk: %s' % words)

    return len(words)


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