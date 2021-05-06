from email.mime.text import MIMEText

import requests
import datetime
import time
import smtplib
import os

SECONDS_TO_SLEEP = 90  # 1.5 minutes

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

now = datetime.datetime.now()
START_DATE = "{}-{}-{}".format(7, now.month, now.year)
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
        print("No new slots found for " + district_name)
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
    subject = "New slots for {} - {}".format(district_name, datetime.datetime.now().strftime("%d-%m-%Y, %H:%M"))
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
            send_email(processed_data, district.get("district_name"))
            time.sleep(15)  # Sleep for 15 seconds between calls
        time.sleep(SECONDS_TO_SLEEP)
