2020/02/13 add in testBranch
111111111
222222222
5.13 change2
333333333

added in master branch

import tweepy
from tweepy import OAuthHandler
import json
import wget
import os


add something again


consumer_key = ' '
consumer_secret = ' '
access_token = ' '
access_secret = ' '


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

tweets = api.user_timeline(screen_name='StephenCurry30',
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
                #print ('converting %s to %s ...' % (src, dst))
                i = i + 1
        #print ('total %d to rename & converted %d jpgs' % (total_num, i))

if __name__ == '__main__':
    newname = ImageRename()
    newname.rename()

os.popen('ffmpeg -r 0.5 -i image%d.jpg -vf scale=-600:600 -y -r 30 -t 60 movie.mp4')
