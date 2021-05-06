import requests
import time
import yagmail

SECONDS_TO_SLEEP = 300  # 5 minutes

state = {
            "state_id": 21,
            "state_name": "Maharashtra"
        }
district = {
                "district_id": 395,
                "district_name": "Mumbai"
            }
START_DATE = "01-05-2021"
headers = {
    "Accept": "application/json",
    "Accept-Language": "en_US",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
}
params = {
    "district": 395,
    "date": START_DATE
}
url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"


def request():
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
                    "cost": r.get("fee_type"),
                    "slots": r.get("slots"),
                    "num_slots": r.get("available_capacity")
                }
                data_to_email.append(row)
    except Exception as e:
        print(e)
    return data_to_email



data = {u'sessions': [{u'address': u'',
                       u'available_capacity': 11,
                       u'block_name': u'Ward R North Corporation - MH',
                       u'center_id': 628041,
                       u'date': u'01-05-2021',
                       u'district_name': u'Mumbai',
                       u'fee': u'0',
                       u'fee_type': u'Free',
                       u'from': u'09:00:00',
                       u'lat': 19,
                       u'long': 72,
                       u'min_age_limit': 45,
                       u'name': u'DAHISAR COVID VACC SUBURBUN',
                       u'pincode': 400068,
                       u'session_id': u'592ee4c2-a13b-496d-87d6-9cbe00665424',
                       u'slots': [u'09:00AM-11:00AM',
                                  u'11:00AM-01:00PM',
                                  u'01:00PM-03:00PM',
                                  u'03:00PM-06:00PM'],
                       u'state_name': u'Maharashtra',
                       u'to': u'18:00:00',
                       u'vaccine': u'COVAXIN'},
                      {u'address': u'',
                       u'available_capacity': 7,
                       u'block_name': u'Ward R North Corporation - MH',
                       u'center_id': 606878,
                       u'date': u'01-05-2021',
                       u'district_name': u'Mumbai',
                       u'fee': u'0',
                       u'fee_type': u'Free',
                       u'from': u'09:00:00',
                       u'lat': 19,
                       u'long': 72,
                       u'min_age_limit': 45,
                       u'name': u'DAHISAR COVID JUMBO -8',
                       u'pincode': 400068,
                       u'session_id': u'bf79efbc-e6b4-40e2-91a2-0d7aa1e54c4c',
                       u'slots': [u'09:00AM-11:00AM',
                                  u'11:00AM-01:00PM',
                                  u'01:00PM-03:00PM',
                                  u'03:00PM-05:00PM'],
                       u'state_name': u'Maharashtra',
                       u'to': u'17:00:00',
                       u'vaccine': u'COVISHIELD'},
                      {u'address': u'',
                       u'available_capacity': 4,
                       u'block_name': u'Ward R North Corporation - MH',
                       u'center_id': 606906,
                       u'date': u'01-05-2021',
                       u'district_name': u'Mumbai',
                       u'fee': u'0',
                       u'fee_type': u'Free',
                       u'from': u'09:00:00',
                       u'lat': 19,
                       u'long': 72,
                       u'min_age_limit': 45,
                       u'name': u'DAHISAR COVID JUMBO -10',
                       u'pincode': 400068,
                       u'session_id': u'87690ffc-36e3-4bf6-b572-f043ca6adb78',
                       u'slots': [u'09:00AM-11:00AM',
                                  u'11:00AM-01:00PM',
                                  u'01:00PM-03:00PM',
                                  u'03:00PM-05:00PM'],
                       u'state_name': u'Maharashtra',
                       u'to': u'17:00:00',
                       u'vaccine': u'COVISHIELD'}]}


def send_email(email_content):
    for row in email_content:
        print(row)


if __name__ == "__main__":
    while True:
        processed_data = parse_data(data)
        # processed_data = parse_data(request())
        send_email(processed_data)
        time.sleep(SECONDS_TO_SLEEP)







