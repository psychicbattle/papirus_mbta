import requests
import os
import pandas as pd
import logging
try:
    from papirus import PapirusTextPos
    PAPIRUS_ENABLED = True
except:
    logging.error("No Papirus found! Will output to stdout.")
    PAPIRUS_ENABLED = False

MBTA_URL = "https://api-v3.mbta.com/"

try:
    API_KEY = os.environ["MBTA_API_KEY"]
except:
    logging.warning("No API key - continuing without. Rate limit will be greatly stricter")
    API_KEY = None


#List of queries (stop ID, route ID):
ROUTES = [(2546, 86), #Washington & Beacon to Sullivan
          (2570, 86), #Washington & Beacon to Reservoir
          (2435, 83),
          (2455, 83)]

FONT_SIZE=17
Y_SHIFT=16
#These configs allow for 5 lines of text on screen and 16 characters

try:
    papirusText = PapirusTextPos(False, rotation=0)
except:
    pass

def strfdelta(tdelta):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    if d["hours"] > 0:
        return f"{d['hours']}h{d['minutes']}m"
    else:
        return f"{d['minutes']}m"
    #return fmt.format(**d)


def query(stop_id, route_id):
    """Just query something!"""
    #rt = pymbta3.Stops(key=API_KEY)
    headers = {"accept": "application/vnd.api+json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    #Get route destinations
    r = requests.get(url=MBTA_URL+f"/routes/{route_id}", headers=headers)
    route = r.json()
    destinations = route["data"]["attributes"]["direction_destinations"]
    #Trim destinations to the first word.
    destinations = [x.split(" ")[0] for x in destinations]
    r = requests.get(url=MBTA_URL+"/predictions",params={"filter[stop]":stop_id,
                                      "filter[route]":route_id}, headers=headers)
    predictions = r.json()
    first_arrival = predictions["data"][0]["attributes"]["arrival_time"]
    direction = predictions["data"][0]["attributes"]["direction_id"]
    first_arrival = pd.Timestamp(first_arrival)
    now = pd.Timestamp("now")
    now = now.tz_localize(first_arrival.tz)
    if first_arrival < now:
        time_str = "Now"
    else:
        time_str = strfdelta(first_arrival - now)
    return(f"{route_id}-{destinations[direction]}: {time_str}")

def send_to_papirus(str_set):
    y = 0
    papirusText.Clear()
    for str in str_set:
        papirusText.AddText(str, 0, y, size=FONT_SIZE)
        y += Y_SHIFT
    papirusText.WriteAll()


if __name__=="__main__":
    display_strs = []
    for stop_id, route_id in ROUTES:
        display_strs.append(query(stop_id, route_id))
    if PAPIRUS_ENABLED:
        send_to_papirus(display_strs)
    else:
        for str in display_strs:
            print(str, len(str))