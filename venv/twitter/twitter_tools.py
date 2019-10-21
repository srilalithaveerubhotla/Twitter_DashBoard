from models import Person
import tweepy
from datetime import datetime, date, time, timedelta

people = []

def twitter_get(screen_name):
    for persons in people:
        if persons.screen_name == screen_name:
            return persons.__dict__

    api = get_api()

    user = None
    try:
        user = api.get_user(screen_name)
    except tweepy.error.TweepError:
        return {"Error":"Username Not Found"}
    tweets_count = user.statuses_count
    account_created_date = user.created_at
    followers_count = user.followers_count

    days = (datetime.utcnow() - account_created_date).days

    timeline = []
    for status in tweepy.Cursor(api.user_timeline, screen_name='@'+screen_name).items():
        timeline.append({"text":status._json["text"],"created_at":status._json["created_at"]})

    avg = float(tweets_count)/float(days)
    persons = Person(screen_name,tweets_count,followers_count,days,timeline,avg)
    people.append(persons)

    return persons.__dict__

def twitter_put(screen_name,message):
    for persons in people:
        if persons.screen_name == screen_name:
            return persons.__dict__

    api = get_api()

    user = None
    try:
        user = api.get_user(screen_name)
    except tweepy.error.TweepError:
        return {"Error":"Username Not Found"}
    status=user.post_data(message)
    persons = Person(status)
    people.append(persons)
    return persons.__dict__

def twitter_delete(screen_name,message):
    for person in people:
        if person.screen_name == screen_name:
            return person.__dict__

    api = get_api()

    user = None
    try:
        user = api.get_user(screen_name)
    except tweepy.error.TweepError:
        return {"Error":"Username Not Found"}
    status = api.destroy_status(message)
    person = Person(status)
    people.append(person)
    return person.__dict__


def get_api():
    consumer_key = 'rH4F3v2sIepDebEgh894gROGV'
    consumer_secret = 'r9pFEWUsZKwHVydWmml5XRPLWwDvuL9wLAjf94Sff8j7XpM86W'

    access_token = '1184571597346107393-G0IlO1JaP5DWtEK7dDSHlnxOTbn8SZ'
    access_token_secret = 'ruwgmkOzMlhfWY9wVu4MgcypqGQu0rggeBDG6nioTXFkf'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    return tweepy.API(auth)