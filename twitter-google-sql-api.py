import tweepy
from tweepy import OAuthHandler
import json
import wget
import os
import io
from google.cloud import vision
from google.cloud.vision import types
import MySQLdb
import pymongo
from datetime import datetime, timedelta


consumer_key = '...'
consumer_secret = '...'
access_token = '...'
access_secret = '... '

jsonpath = ''  #path of json fole 
imgpath = '' #path of the image


#establish the connection to mysql databse and create database
try:
	db = MySQLdb.connect(host='localhost', user='', passwd='')
	cursor = db.cursor()

	cursor.execute("""create database if not exists python;""")
except Exception as e:
	print("Create mysql database error ", e)

#create mysql table
try:
	sql = """"CREATE TABLE IF NOT EXISTS information(run_time NOT NULL, user_info NOT NULL, tweet_num NOT NULL, picture_num NOT NULL, label_each NOT NULL);"""
	cursor.execute(sql)
except Exception as e:
	print("Create mysql table error", e)


#establish the connection to mongodb
try:
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	mydb = myclient["runoobdb"]

	mycol = mydb["apimongo"]
except Exception as e:
	print("Create MOngodb error", e)


#catch time when a user runs the program and store the data into database
now_time = datetime.now()
try:
	cursor.execute("INSERT INTO information (run_time) VALUES(%s);", %(now_time))
    db.commit()
    #insert num of picture into mongodb
    time = {'runtime': 'now_time'}
    mycol.insert_one(time)
except Exception as e:
	print("catching time error", e)



@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status
 
# Status() is the data model for a tweet
tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse
# User() is the data model for a user profil
tweepy.models.User.first_parse = tweepy.models.User.parse
tweepy.models.User.parse = parse
# You need to do it for all the models you need

 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)



#for status in tweepy.Cursor(api.home_timeline).items(10):
 #   print(status.text)

user_name = 'StephenCurry30'  #You can change the tweeter user, I choose Stephen Curry's tweet here
#insert user_name into database
try:
    cursor.execute("INSERT INTO information (user_info) VALUES(%s);", %(user_name))
    db.commit()
    #insert num of picture into mongodb
    userinfo = {'userinformation': 'user_name'}
    mycol.insert_one(userinfo)
except Exception as e:
    print("error when inserting username into database", e)

#get tweets from the user
tweets = api.user_timeline(screen_name=user_name,
                           count=20, include_rts=False,
                           exclude_replies=True)

media_files = set()
for status in tweets:
    media = status.entities.get('media', [])
    if(len(media) > 0):
        media_files.add(media[0]['media_url'])

for media_file in media_files:
    wget.download(media_file)

class ImageRename():
    def __init__(self):
        self.path = '/home/ece-student/EC601/'

    def rename(self):
        filelist = os.listdir(self.path)
        total_num = len(filelist)

        i = 0

        for item in filelist:
            if item.endswith('.jpg'):
                src = os.path.join(os.path.abspath(self.path), item)
                dst = os.path.join(os.path.abspath(self.path), 'image' + format(str(i), '0>1s') + '.jpg')
                os.rename(src, dst)
                print ('converting %s to %s ...' % (src, dst))
                i = i + 1
        print ('total %d to rename & converted %d jpgs' % (total_num, i))
        

        try:
	        #insert number of tweets and number of picture been converted into mysql database
	        cursor.execute("INSERT INTO information (tweet_num, picture_num) VALUES(%s, %s);", %(total_num, i))
	        db.commit()
	        #insert num of picture into mongodb
	        numdata = {'tweetnum': 'tweet_num', 'picnum': 'picture_num'}
	        mycol.insert_one(numdata)
	    except Exception as e:
	    	print("insert numdata into database error", e)


def google_label(jsonpath, imgpath):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = jsonpath
    client = vision.ImageAnnotatorClient()

    img_list = os.listdir(os.getcwd())
    for img in img_list:
        if img.endswith('.jpg'):
            ylb = 50
            img_path = os.path.join(os.path.abspath(os.getcwd()), img)
            file_name = os.path.join(
                os.path.dirname(__file__), img_path)


            with io.open(file_name, 'rb') as image_file:
                content = image_file.read()
            image = types.Image(content=content)

            try:
                response = client.label_detection(image=image)
                labels = response.label_annotations
            except:
                print("label error")
                os._exit(0)

            try:
            	#insert label into mysql database
                cursor.execute("INSERT INTO information (label_each) VALUES(%s);", %labels)
        		db.commit()
        		#insert label into mongodb
        		labeldata = {'labeldata': 'label_each'}
        		mycol.insert_one(labeldata)
        	except Exception as e:
        		print("insert labeldata into databese error", e)

            print(img + "'s Labels:")

            for label in labels:
                image = Image.open(img)
                # initialise the drawing context with
                # the image object as background
                draw = ImageDraw.Draw(image)
                # create font object with the font file and specify
                # desired size
                font = ImageFont.truetype('GillSans.ttc', size=45)
                # starting position of the message
                (x, y) = (50, ylb)
                message = label.description
                color = 'rgb(250, 250, 250)'  # white color
                # draw the message on the background
                draw.text((x, y), message, fill=color, font=font)
                ylb = ylb + 50
                image.save(img)
                print(label.description)
            print('\n')


#look up the label in database, word can be changed through changing lookupword
lookupword = "basketball"  #you can change the label name, here I use basketball just as an example
def lookuplabel():
    sql = "SELECT * FROM information WHERE label_each == lookupword;"
    try:
        cursor.execute("SELECT * FROM information WHERE label_each == %s;", %lookupword)
        results = cursor.fetchall()
        for row in results:
            name = row[1]
            print("(mysql)User: %s has the picture labeld as %s" %(name, lookupword))
    except Exception as e:
        print("mysql error when looking up one label", e)

    try:
        for x in mycol.find{}, {"labeldata": lookupword}:
            print("(mongodb)User: %d has the picture labeled as %d" %(x, lookupword))
    except Exception as e:
        print("mongodb error when looking up one label", e)

def lookup_mostpop():
    try:
        sql = "SELECT label_each, count(*) as count from information group by label_each order by count desc limit 1;"
        results = cursor.execute(sql)
        print("%s is the most popular label in databse", %results)
    except Exception as e:
        print("error when finding most popular label", e)



if __name__ == '__main__':
    newname = ImageRename()
    newname.rename()
    google_label(jsonpath, imgpath)
    lookuplabel()
    lookup_mostpop()

#convert all the pictures to movie
os.popen('ffmpeg -r 0.5 -i image%d.jpg -vf scale=-600:600 -y -r 30 -t 60 movie.mp4')

#close the mysql database
db.close()