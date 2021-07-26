try:
    from Tkinter import *
    import ttk
    import Tkinter as tk
except ImportError:
    from tkinter import *
    from tkinter import ttk
    import tkinter as tk

import requests
import json
import webbrowser
import time

import threading
from tkcalendar import Calendar, DateEntry
from datetime import datetime, timedelta
from dateutil import parser

global currentURL
global linkButton

# TODO add update in getTimeSelected for when u change location and/or sport
# TODO add eventID as now there's multiple events with same name at same time

def waitTime(bookingDate, holdURL):
    while (datetime.now() <= bookingDate):
        if (datetime.now() >= bookingDate - timedelta(minutes=1)):
            continue
        time.sleep(55)
    webbrowser.open(holdURL, new=2)
    bookingLabel['text'] = "Opening page at {0}, hope you got it!".format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    submitButton['state'] = NORMAL

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

def timeSelected(*args):
    if (timeOption == ''):
        linkButton['state'] = DISABLED
        return
    url = 'https://cityofcoquitlam.perfectmind.com/Contacts/BookMe4BookingPagesV2/CoursesV2'
    myobj = {
        'calendarId': 'd46c79d5-59b1-45c2-b9ee-e816895bddf9', #updated calendarId in v3.0
        'widgetId': '15f6af07-39c5-473e-b053-96653f77a406'
    }
    response = requests.post(url, data=myobj)
    data = json.loads(response.text)
    holdURL = None
    splitList = timeOption.get().split("ID:")
    selectedTime = splitList[0].strip()
    selectedEvent = splitList[-1].strip()
    for session in data:
        ourDate = custom_strftime("%b {S}", datetime.strptime(dateButton['text'], "%b %d"))
        if (int(session["MinAge"]) == 19 and selectedSport.get().lower() in str(session["EventName"]).lower() and selectedLocation.get().lower() in str(session["Location"]).lower()
                and ourDate in str(session["FormattedStartDate"]) and selectedTime in str(session["EventTimeDescription"]) and selectedEvent in str(session["CourseIdTrimmed"])):
            holdURL = 'https://cityofcoquitlam.perfectmind.com/Contacts/BookMe4EventParticipants?eventId={0}&widgetId=15f6af07-39c5-473e-b053-96653f77a406&locationId=5524cc20-9310-4a91-9ae5-87b2585c82f5'.format(
                str(session["EventId"]))
            break
    global currentURL
    currentURL = holdURL

def calendar():
    top = Toplevel(app)

    now = datetime.now()
    cal = Calendar(top,
                   font="Arial 14", selectmode='day',
                   cursor="hand1", year=now.year, month=now.month, day=now.day)
    cal.pack(fill="both", expand=True)

    def closeCalendar():
        top.destroy()
        top.update()
        dateButton['text'] = cal.selection_get().strftime("%b %d")
        getAvailableTimes()

    ttk.Button(top, text="ok", command=closeCalendar).pack()

def placeholder(event):
    getAvailableTimes()

def getAvailableTimes():
    try:
        url = 'https://cityofcoquitlam.perfectmind.com/Contacts/BookMe4BookingPagesV2/CoursesV2' #updated url link in v3.0
        myobj = {
            'calendarId': 'd46c79d5-59b1-45c2-b9ee-e816895bddf9', #updated calendarId in v3.0
            'widgetId': '15f6af07-39c5-473e-b053-96653f77a406'
        }

        response = requests.post(url, data=myobj)
        data = json.loads(response.text)
        timeMenu['menu'].delete(0, 'end')
        timeOption.set('')
        selectedTime = ''
        global currentURL
        currentURL = ''
        found = FALSE
        for session in data:
            ourDate = custom_strftime("%b {S}", datetime.strptime(dateButton['text'], "%b %d"))
            if (int(session["MinAge"]) == 19 and selectedSport.get().lower() in str(session["EventName"]).lower() and selectedLocation.get().lower() in str(session["Location"]).lower() #changed Location tag in v3.0
                    and ourDate in str(session["FormattedStartDate"])):
                choice = str(session["EventTimeDescription"]) + " ID:" + str(session["CourseIdTrimmed"])
                timeMenu['menu'].add_command(
                    label=choice, command=tk._setit(timeOption, choice))
                found = TRUE
        if not found:
            timeMenu['menu'].add_command(
                label='', command=tk._setit(timeOption, ''))
    except Exception as e:
        print(e)


def submit():
    try:
        url = 'https://cityofcoquitlam.perfectmind.com/Contacts/BookMe4BookingPagesV2/CoursesV2' #updated url link in v3.0
        myobj = {
            'calendarId': 'd46c79d5-59b1-45c2-b9ee-e816895bddf9', #updated calendarId in v3.0
            'widgetId': '15f6af07-39c5-473e-b053-96653f77a406'
        }

        sportMenu['state'] = DISABLED
        locationMenu['state'] = DISABLED
        dateButton['state'] = DISABLED
        timeMenu['state'] = DISABLED

        response = requests.post(url, data=myobj)
        data = json.loads(response.text)
        holdURL = None
        currentSession = None
        selectedEvent = timeOption.get().split("ID:")[1].strip()
        for session in data:
            ourDate = custom_strftime("%b {S}", datetime.strptime(dateButton['text'], "%b %d"))
            if (int(session["MinAge"]) == 19 and selectedSport.get().lower() in str(session["EventName"]).lower() and selectedLocation.get().lower() in str(session["Location"]).lower()
                    and ourDate in str(session["FormattedStartDate"]) and selectedTime in str(session["EventTimeDescription"]) and selectedEvent in str(session["CourseIdTrimmed"])):
                holdURL = 'https://cityofcoquitlam.perfectmind.com/Contacts/BookMe4EventParticipants?eventId={0}&widgetId=15f6af07-39c5-473e-b053-96653f77a406&locationId=5524cc20-9310-4a91-9ae5-87b2585c82f5'.format(
                    str(session["EventId"]))
                currentSession = session
        if holdURL:
            noticeLabel['text'] = "If you keep me running, I will automatically reserve the spot for you at the start time!"
            noticeLabel['text'] += "\nMake sure you've logged into the page a few minutes before the start time!"
            bookingLabel['text'] = ''

            current = datetime.now()
            bookingDate = parser.parse(str(
                current.year) + " " + dateButton['text'] + " " + currentSession["FormattedStartTime"]) - timedelta(days=2)
            if (current.date() < bookingDate.date()):
                noticeLabel['text'] = ''
                bookingLabel['text'] = "This booking is more than 2 days ahead, please try another booking"
                return

            bookingLabel['text'] = "Waiting to snipe your spot at " + \
                currentSession["FormattedStartTime"] + "..."
            submitButton['state'] = DISABLED
            x = threading.Thread(target=waitTime, kwargs={
                                 'bookingDate': bookingDate,
                                 'holdURL': holdURL})
            x.daemon = TRUE
            x.start()
            global currentURL
            currentURL = holdURL
        else:
            bookingLabel['text'] = "URL was not found :( sad"
    except Exception as e:
        print(e)

def openURL():
    if (currentURL != ''):
        webbrowser.open(currentURL, new=2)


def onClose():
    app.destroy()
    exit()

app = Tk()
app.title('Booking System')
app.protocol("WM_DELETE_WINDOW", onClose)
# You can set the geometry attribute to change the root windows size
app.geometry("520x270")
app.resizable(1, 1)  # Allow resizing in the x or y direction

'''
Setup the area to input booking information
  - bookingInfo Frame - top half
'''
bookingInfo = Frame(app, bd=1, relief="solid")
bookingInfo.grid(row=0, column=0, pady=5, padx=110)

# Dictionary with options

selectedSport = StringVar(bookingInfo)
sports = {'Volleyball', 'Basketball'}
selectedSport.set('Volleyball')  # set the default option
sportMenu = OptionMenu(bookingInfo, selectedSport, *sports, command=placeholder)

selectedLocation = StringVar(bookingInfo)
locations = {'Pinetree', 'Centennial'}
selectedLocation.set('Pinetree')  # set the default option
locationMenu = OptionMenu(bookingInfo, selectedLocation, *locations, command=placeholder)

timeOption = StringVar(bookingInfo)
selectedTime = ''
timeList = {''}
timeOption.set('')  # set the default option
timeMenu = OptionMenu(bookingInfo, timeOption, *timeList)
timeOption.trace("w", timeSelected)

Label(bookingInfo, text="Select Location").grid(row=0, column=0)
locationMenu.grid(row=0, column=1)

Label(bookingInfo, text="Select Sport").grid(row=1, column=0)
sportMenu.grid(row=1, column=1)

Label(bookingInfo, text="Select Date").grid(row=2, column=0)
dateButton = Button(bookingInfo, text=datetime.now(
).date().strftime("%b %d"), command=calendar)
dateButton.grid(row=2, column=1)

getAvailableTimes()
Label(bookingInfo, text="Select Time").grid(row=3, column=0)
timeMenu.grid(row=3, column=1)

currentURL = ''
linkButton = Button(bookingInfo, text="URL", command=openURL)
linkButton.grid(row=3, column=2, padx=5)

submitButton = Button(bookingInfo, text="Find Booking", command=submit)
submitButton.grid(row=5, column=0, columnspan=3, pady=20)

'''
Setup Labels
'''
textFrame = Frame(app)
textFrame.grid(row=1, column=0)
noticeLabel = Label(textFrame, text="")
noticeLabel.grid(row=0, column=0, sticky=W)
bookingLabel = Label(textFrame, text="")
bookingLabel.grid(row=1, column=0)

if __name__ == "__main__":
    app.mainloop()
