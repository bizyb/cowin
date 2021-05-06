import requests
import datetime
import time
import smtplib
import os

SECONDS_TO_SLEEP = 1800  # 30 minutes

state = {
            "state_id": 21,
            "state_name": "Maharashtra"
        }
district = {
                "district_id": 394,
                "district_name": "Palghar"
            }
now = datetime.datetime.now()
START_DATE = "{}-{}-{}".format(now.day, now.month, now.year)
headers = {
    "Accept": "application/json",
    "Accept-Language": "en_US",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
}
params = {
    "district_id": 394,
    "date": START_DATE
}
url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"


def request():
    session = requests.Session()
    session.headers.update(headers)
    response = session.get(url, params=params)
    print(response.json())
    return response.json()


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
                    "slots": r.get("slots"),
                    "num_slots": r.get("available_capacity")
                }
                data_to_email.append(row)
    except Exception as e:
        print(e)
    return data_to_email


def send_email(email_content):
    body = ""
    if not email_content:
        body = "No slots found"
    for ec in email_content:
        slots = "\n".join(["\t" + slot for slot in ec.get("slots")])
        text = "Location: {}\nCost: {}\nNumber of Slots: {}\nDate: {}\n\n".format(
            ec.get("location").replace("\n", ""),
            ec.get("cost"),
            ec.get("num_slots"),
            ec.get("date"))
        body += text
    print("About to send email...")
    print("Email body: ", body)
    gmail_user = os.environ.get('EMAIL_USER')
    gmail_pwd = os.environ.get('EMAIL_PASSWORD')
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    mailing_list = [e for e in os.environ.get('MAILING_LIST').split(",") if e]
    for to in mailing_list:
        tag = datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
        if not email_content:
            tag = "--No slots found--"
        header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:CoWIN Vaccination Slots {}\n'\
            .format(tag)
        print(header)
        msg = header + '\n {} \n\n'.format(body)
        smtpserver.sendmail(gmail_user, to, msg)
        print("Email sent to " + to)
    smtpserver.close()


if __name__ == "__main__":
    while True:
        processed_data = parse_data(request())
        send_email(processed_data)
        time.sleep(SECONDS_TO_SLEEP)