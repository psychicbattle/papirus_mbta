import requests
import os
import pandas as pd
import logging
try:
    from papirus import PapirusTextPos
except:
    pass
MBTA_URL = "https://api-v3.mbta.com/predictions"

try:
    API_KEY = os.environ["MBTA_API_KEY"]
except:
    logging.warning("No API key - continuing without. Rate limit will be greatly stricter")
    API_KEY = None

STOP_ID = 2546
ROUTE_ID = 86

try:
    papirusText = PapirusTextPos(rotation=0)
except:
    pass

def strfdelta(tdelta):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    if d["hours"] > 0:
        return f"{d['hours']} hours, {d['minutes']} min"
    else:
        return f"{d['minutes']} min"
    #return fmt.format(**d)


def simple_test():
    """Just query something!"""
    #rt = pymbta3.Stops(key=API_KEY)
    headers = {"accept": "application/vnd.api+json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    r = requests.get(url=MBTA_URL,params={"filter[stop]":STOP_ID,
                                      "filter[route]":ROUTE_ID}, headers=headers)
    json = r.json()
    first_arrival = json["data"][0]["attributes"]["arrival_time"]
    first_arrival = pd.Timestamp(first_arrival)
    now = pd.Timestamp("now")
    now = now.tz_localize(first_arrival.tz)
    time_str = strfdelta(first_arrival - now)
    try:
        send_to_papirus("86 to Sullivan: " + time_str)
    except:
        pass

def send_to_papirus(str):
    papirusText.write(str)

if __name__=="__main__":
    simple_test()