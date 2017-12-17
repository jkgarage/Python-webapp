WTF_CSRF_ENABLED = True
SECRET_KEY = 'my_secret_key_betyoudontknow'

EMAIL_ADDRESS_FROM = 'admin@jkgarage-home.appspotmail.com'
CONTACT_ME_SEND_TO = 'jingkee+jkgarage@gmail.com'

DATA_PATH = 'data/'
HSK_FILE_PATH = DATA_PATH + 'full_hsk.csv'

ENGLISH_STOPWORDS = [u'i', u'me', u'my', u'myself', u'we', u'our', u'ours',
  u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he',
  u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', 
  u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', 
  u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', 
  u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have',
  u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an',
  u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while',
  u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between',
  u'into', u'through', u'during', u'before', u'after', u'above', u'below',
  u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over',
  u'under', u'again', u'further', u'then', u'once', u'here', u'there',
  u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each',
  u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not',
  u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't',
  u'can', u'will', u'just', u'don', u'should', u'now', u'd', u'll', u'm',
  u'o', u're', u've', u'y', u'ain', u'aren', u'couldn', u'didn', u'doesn',
  u'hadn', u'hasn', u'haven', u'isn', u'ma', u'mightn', u'mustn', u'needn',
  u'shan', u'shouldn', u'wasn', u'weren', u'won', u'wouldn', u'I', u'You', 
  u'He', u'She', u'We', u'They']

FORMAT_PER_HSK_LEVEL = {'1':'hsk1', '2':'hsk2', '3':'hsk3', '4':'hsk4',
'5':'hsk5','6':'hsk6','name':'zh-name','cdict':'zh-cdict'}
HSK_MAX_LENG = 5

UPLOAD_PATH = 'photos/'