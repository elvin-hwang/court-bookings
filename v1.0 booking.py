try:
    from Tkinter import *
except ImportError:
    from tkinter import *

import requests
import json
import webbrowser 
import time
from datetime import datetime, timedelta
from dateutil import parser

try:
    input = raw_input
except NameError:
    pass

print("\nPress Enter to keep the [default value], or input a value with the same format\n")

eventName = input(
    "Sport: [Badminton Court] ").strip() or "Badminton Court" # "Table Tennis Court", "Badminton Court"
location = input(
    "Location: [Pinetree] ").strip() or "Pinetree" # Centennial

date = input(
    "Date: [Apr 14th] ").strip() or "Apr 14th" # Change this if you want a new default value
startTime = input(
    "StartTime: [5:30PM] ").strip() or "5:30PM" # Change this if you want a new default value

try:
    url = 'https://cityofcoquitlam.perfectmind.com/Contacts/BookMe4BookingPages/Courses'
    myobj = {
        'calendarId': '1e692aed-988d-4257-958e-7deee5275ccc',
        'widgetId': '15f6af07-39c5-473e-b053-96653f77a406'
    }

    response = requests.post(url, data=myobj)
    data = json.loads(response.text)
    holdURL = None
    for session in data:
        print(session)
        if (int(session["MinAge"]) == 19 and eventName.lower() in str(session["EventName"]).lower() and location.lower() in str(session["EventName"]).lower()
                and str(session["FormattedStartDate"]) == date and str(session["FormattedStartTime"]) == startTime):
            holdURL = 'https://cityofcoquitlam.perfectmind.com/Contacts/BookMe4EventParticipants?eventId={0}&widgetId=15f6af07-39c5-473e-b053-96653f77a406&locationId=5524cc20-9310-4a91-9ae5-87b2585c82f5'.format(
                str(session["EventId"]))
            print("\n" + holdURL + "\n")
            # print(json.dumps(session, skipkeys=True, indent=4))
    if holdURL:
        # webbrowser.open(holdURL, new=2)
        # payload = {'username': 'hosung0519@hotmail.com', 'password': '2865285Hs.'}
        # url = 'https://cityofcoquitlam.perfectmind.com/SocialSite/MemberRegistration/MemberSignIn'
        # response = requests.post(url, data=payload)
        # print(response.content)
        # webbrowser.open(holdURL, new=2)

        print("\nIf you keep me running, I will automatically reserve the spot for you at the start time!")

        current = datetime.now()
        bookingDate = parser.parse(str(current.year) + " " + date + " " + startTime) - timedelta(days=2)
        if (current.date() < bookingDate.date()):
            print("\nPlease try again closer to the booking date/time!\n")
            exit(0)

        print("Make sure you've logged into the page before the start time!\n")
        print("waiting to snipe your spot at " + startTime + "...")
        while (datetime.now() < bookingDate):   
            if (datetime.now() >= bookingDate - timedelta(minutes=1)):
                continue
            time.sleep(55)

        webbrowser.open(holdURL, new=2)
        print("\nOpening page, hope you got it!\n")     
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))          
    else :
        print("\nURL was not found :( sad \n")

except Exception as e:
    print(e)
    
def onClose():
  print('...Closing UBC Course Checker UI...')
  for process in processes:
    process.stop()
  app.destroy()
  sys.exit()

processes = []
app = Tk()
app.title('UBC Course Checker')
app.protocol("WM_DELETE_WINDOW", onClose)
#You can set the geometry attribute to change the root windows size
app.geometry("750x560")
app.resizable(1, 1) #Allow resizing in the x or y direction

