from email.mime.text import MIMEText

import requests
import datetime
import pytz
import time
import smtplib
import os
import tweepy
from tweepy import TweepError

CONTENT_THRESHOLD = 500
# Keep up to 500 entries in memory
in_mem_db = {}
in_mem_db_list = []

TWITTER_API_CONSUMER_KEY = os.environ.get('TWITTER_API_CONSUMER_KEY')
TWITTER_API_CONSUMER_SECRET = os.environ.get('TWITTER_API_CONSUMER_SECRET')
TWITTER_API_ACCESS_TOKEN = os.environ.get('TWITTER_API_ACCESS_TOKEN')
TWITTER_API_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_API_ACCESS_TOKEN_SECRET')

SECONDS_TO_SLEEP = 300  # 5 minutes

state = {
    "state_id": 21,
    "state_name": "Maharashtra"
}
districts = [
    {
        "district_id": 395,
        "district_name": "Mumbai"
    },
    {
        "district_id": 394,
        "district_name": "Palghar"
    },
]
IST = pytz.timezone('Asia/Kolkata')
now = datetime.datetime.now(IST)
START_DATE = "{}-{}-{}".format(now.day, now.month, now.year)
headers = {
    "Accept": "application/json",
    "Accept-Language": "en_US",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
}

url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"


def request(district_id):
    params = {
        "district_id": district_id,
        "date": START_DATE
    }
    session = requests.Session()
    session.headers.update(headers)
    response = session.get(url, params=params)
    try:
        return response.json()
    except Exception as e:
        print("response.json() has no data: ", e)
        return {}


def parse_data(json_data):
    data_to_email = []
    try:
        results = json_data.get("sessions")
        if results:
            for r in results:
                row = {
                    "location": "{}, {}, {}".format(r.get("name"), r.get("block_name"), r.get("district_name")),
                    "date": r.get("date"),
                    "cost": r.get("fee"),
                    "slots": "\n" + "\n".join(["\t" + s for s in r.get("slots")]),
                    "num_slots": r.get("available_capacity")
                }
                data_to_email.append(row)
    except Exception as e:
        print("Unable to parse response: ", e)
    return data_to_email


def update_db(content_hash):
    # Do not tweet if content already in db
    if content_hash in in_mem_db:
        return False

    if len(in_mem_db) == CONTENT_THRESHOLD:
        value_to_delete = None
        if len(in_mem_db_list) > 0:
            value_to_delete = in_mem_db_list[0]
            del in_mem_db_list[0]
        if value_to_delete:
            del in_mem_db[value_to_delete]

    in_mem_db[content_hash] = True
    in_mem_db_list.append(content_hash)
    return True


def tweet(content, district_name):
    auth = tweepy.OAuthHandler(TWITTER_API_CONSUMER_KEY, TWITTER_API_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_API_ACCESS_TOKEN, TWITTER_API_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    for c in content:
        location = c.get("location").replace("\n", "")
        cost = c.get("cost")
        num_slots = c.get("num_slots")
        date = c.get("date")
        time_window = c.get('slots')
        content_hash = hash("{}-{}-{}-{}-{}-{}".format(location, cost, num_slots, date, district_name, time_window))
        do_tweet = update_db(content_hash)
        if do_tweet:
            status = "New vaccination slots for the {} district\n\nLocation: {}\nDate: {}\nNumber of Slots: {}\nCost: {}\n{}".format(
                district_name,
                location,
                date,
                num_slots,
                cost,
                time_window,
            )
            try:
                api.update_status(status)
            except TweepError as e:
                print("Tweepy error: ", e)
            print("New tweet: ", status)
            time.sleep(5)  # Sleep for 5 seconds between tweets


def send_email(email_content, district_name):
    body = ""
    for ec in email_content:
        slots = "\n".join(["\t" + slot for slot in ec.get("slots")])
        text = "Location: {}\nCost: {}\nNumber of Slots: {}\nDate: {}\n\n".format(
            ec.get("location").replace("\n", ""),
            ec.get("cost"),
            ec.get("num_slots"),
            ec.get("date"))
        body += text
    if not email_content:
        body = "No new slots found for " + district_name
        print(body)
        return

    print("Email body: ", body)
    email_address = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASSWORD')
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(email_address, password)

    mailing_list = [e for e in os.environ.get('MAILING_LIST').split(",") if e]
    subject = "New slots for {} - {}".format(district_name, datetime.datetime.now(IST).strftime("%d-%m-%Y, %H:%M"))
    if not email_content:
        subject = "No slots found for {}".format(district_name)
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "CoWIN Vaccination Alert <{}>".format(email_address)
    for to in mailing_list:
        msg['To'] = to
        smtpserver.sendmail(email_address, to, msg.as_string())
        print("Email sent to " + to)
    smtpserver.close()
    print("Done")


if __name__ == "__main__":
    while True:
        for district in districts:
            print("New search for " + district.get("district_name"))
            processed_data = parse_data(request(district.get("district_id")))
            if processed_data:
                print("Attempting to tweet processed data")
                tweet(processed_data, district.get("district_name"))
            else:
                print("No data to tweet")
            print("Sleeping for 15 seconds between districts")
            time.sleep(15)  # Sleep for 15 seconds between calls
        print("Sleeping for {} minutes between searches".format(SECONDS_TO_SLEEP/60))
        time.sleep(SECONDS_TO_SLEEP)
