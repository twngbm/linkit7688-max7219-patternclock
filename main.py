# -*- coding: utf-8 -*-
import serial
import datetime
import json
import time
import os
message = [0, 0, 0, 0]
looper = 0

# Change event bitmask into list
# "01010" will change into [2,4]


def event_to_list(event):
    events = event[6:]
    event_list = []
    for idx, item in enumerate(events):
        if item == "1":
            event_list.append(idx+1)
    return event_list


def setup():
    global s
    global data, json_index
    global time_shift
    global alarm_dict
    global immediately_start_time

    # Handling timezone not in UTC+8
    # Define timezone here (UTC+8 for Taiwan)
    timezone = 8
    time_shift = (timezone*60*60)-(-time.timezone)

    # Try opening in serial port
    # Other wise output message to STDOUT
    
    s = serial.Serial("/dev/ttyS0", 57600)
    

    # Read file from .json
    with open("/root/Schedule.json") as json_file:
        data = json.loads(json_file.read())
    
    # Turn events bitmask into dictionary structure
    # alarm_dict = { str event_start_time : [ int index, str event_end_time, list [ int event_number ], int position ] }
    # An event at 18:30 with event bitmask:10010210101 will turn into
    # {"17:30":[0,"18:30",[1,3,5],2]}
    # which index may change depend on real index
    json_index = list(data.keys())
    alarm_dict = {}
    for item in json_index:
        # Get event from json Ex : "10001210101"
        event = event_to_list(str(data[item]["events"]))
        # Calculate event start time
        # Ex: An event end at 18:30 will be break down into
        # hh="17"
        # mm="30"
        hh = str((datetime.datetime.strptime(
            str(data[item]["hour"]), "%H")-datetime.timedelta(hours=1)).hour)
        mm = str(data[item]["minute"])
        # Get position of which MXA7219 should light up
        # Ex: An event end at 18:30 will have position 2
        # Since minute 30 should be set at THIRD MXA7219(position 2)
        position = str(data[item]["events"])[1:5].index("1")
        alarm_dict[hh+":"+mm] = [item,
                                 str(data[item]["hour"])+":"+str(data[item]["minute"]), event, position]

    
    flag = ["0", "0", "0", "0"]
    # Determin if there are any event should wake up immediately
    # By setting flag with start time
    # For example, if now time is 18:30 and a 19:15 event should wake up immediately
    # Than flag will become ["0","19:15","0","0"]
    # If therer are multi event should wake up immediately
    # Than flag will be set up multi time.
    # Be aware of the item index been set up to event_start_time is the same as the position in alarm_dict
    # Position means which MXA7219 should be set up for.
    # In the above example, minutes 15 means second MXA7219 should be set up
    # which is the same as the position of event_start_time in flag.
    for times in alarm_dict:
        # Get Now time
        now = datetime.datetime.now()+datetime.timedelta(seconds=time_shift)
        ymd = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
        # Get an event_start_time
        begin_time = datetime.datetime.strptime(
            ymd+" "+times+":"+'0', "%Y-%m-%d %H:%M:%S")
        # Get an event_end_time
        end_time = datetime.datetime.strptime(
            ymd+" "+alarm_dict[times][1]+":"+'0', "%Y-%m-%d %H:%M:%S")
        # Determint if there are any event_start_time between Now time and event_end_time
        # Than set flag to event_start_time
        if (begin_time-now).total_seconds() <= 0 and (end_time-now).total_seconds() >= 0:
            immediately_start_time = times
            flag[alarm_dict[times][3]] = immediately_start_time
    print(alarm_dict)
    print(flag)

    return flag


def loop(flag):
    global message
    global looper
    # Get Now time in hh:mm format
    now = datetime.datetime.now()+datetime.timedelta(seconds=time_shift)
    current_hour, current_minute = str(now.hour), str(now.minute)
    current_time = current_hour+":"+current_minute
    # Travel through all event
    # If current time match event in alarm_dict
    # Add it to flag
    for start_time in alarm_dict:
        if current_time == start_time:  # start of event
            flag[alarm_dict[start_time][3]] = current_time

    # Travel through flag and determint which event should be handle.
    for idx, start_time in enumerate(flag):
        # flag[idx]== "0" means there are current not event on that time.
        if start_time == "0":
            message[idx] = 0
        # Handle enent which is alive
        elif start_time != "0":
            # Handle NULL event
            if len(alarm_dict[start_time][2]) == 0:
                message[idx] = 0
            # Save an event to message
            else:
                message[idx] = alarm_dict[start_time][2][looper %
                                                         len(alarm_dict[start_time][2])]
            # If current_time is event_end_time, set flag[idx]="0" to clear event in flag
            if current_time == alarm_dict[start_time][1]:
                flag[idx] = "0"
    #Do a looper++, looper will help chosen an event in event list
    looper += 1
    looper %= 60
    
    # Bring up message and turn into a string
    s_message = str(message[0])+str(message[1])+str(message[2])+str(message[3])
    
    # Write message to serial port.
    s.write((s_message+"\n"))
    print(s_message)


    time.sleep(2)


if __name__ == '__main__':
    os.system("ntpd -q -p ptbtime1.ptb.de")
    flag = setup()
    cou=0
    while True:
        loop(flag)
	if cou==0:
	    os.system("ntpd -q -p ptbtime1.ptb.de")
        cou+=1
        cou%=120
