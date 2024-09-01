import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox, RadioButtons
import numpy as np
import pyrebase
from time import sleep
from collections import OrderedDict
import time
import smtplib

email = "ece.4880.lab@gmail.com"
password = "KK5PF6qc9GKWhT"

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(email, password)

def send_sms(number, message):
    server.sendmail(email, number, message)

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://ece-4880-lab1-default-rtdb.firebaseio.com/",
  "storageBucket": "projectId.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
def send_button_press(db, change):
    db.child("ReadTemperatureButton").set(change)

def get_read_temperature_button(db):
    return db.child("ReadTemperatureButton").get().val()

def set_read_temperature_button(db, state):
    if state != 0 and state != 1:
        return
    
    db.child("ReadTemperatureButton").set(state)
def get_stored_temperatures(db):
    temp_data = db.child("Temperature").get().val()
    time_data = db.child("Time").get().val()

    final_temp_data = []
    final_time_data = []
    for element in temp_data:
        final_temp_data.append(temp_data[element])

    for element in time_data:
        final_time_data.append(time_data[element])

    return np.array(final_temp_data), np.array(final_time_data)

    # set_temp(db, 10)

#getting the stored temperatures
a, Time = get_stored_temperatures(db)
send_button_press(db,0)

#test to convert array to float
e = np.array(['nil', 'nil', 3, 4, 5])
f = np.array([])
for x in e:
    if x == 'nil':
        f = np.append(f, None)
    else:
        f = np.append(f,float(x))
#print(f)

#should convert array to float
temp = np.array([])
for i in a:
    if i == 'nil':
        temp = np.append(temp, None)
    else:
        temp = np.append(temp,float(i))
if temp.size == 301:
    temp = np.delete(temp, 0)
temp = np.flip(temp)
#print(temp)



plt.ion()
fig, ax = plt.subplots(sharex = True)
x = np.arange(1,301)
line1, = ax.plot(x,temp, 'b-')
plt.gcf().set_size_inches(14, 10)
 

ax.invert_xaxis()
ax.set_ylim([10,50])
ax.set_title("Temperature Data")
ax.set_xlabel("Time (seconds ago)")
ax.set_ylabel("Temperature in C")
 

def on_click(event):
    if ("Temperature in C" in ax.get_ylabel()):
        ax.set_ylabel("Temperature in F")
        ax.set_ylim([50,122])
    else:
        ax.set_ylabel("Temperature in C")
        ax.set_ylim([10,50])
    #fig.canvas.draw()
    #fig.canvas.flush_events()

def on_click1(event):
    if get_read_temperature_button(db) == 0:
       set_read_temperature_button(db,1)
    else:
        set_read_temperature_button(db,0)
print("button test")
print(get_read_temperature_button)
attcarrier = '@mms.att.net'
vercarrier = '@tmomail.net'
tmobcarrier = '@vtext.com'
uscarrier = '@email.uscc.net'
def change_carriers(label):
    if label == 'AT&T':
        carrier = '@mms.att.net'
        return carrier
    elif label == 'T-Mobile':
        carrier = '@tmomail.net'
        return carrier
    elif label == 'Verizon':
        carrier = '@vtext.com'
        return carrier
        
    
    

#defining real time temperature textbox
graphBox = fig.add_axes([0.3, 0.92, 0.5, 0.075])
txtBox = TextBox(graphBox, "Temperature: ")
txtBox.set_val(str(temp[0]) + " Degrees C")

#defining min temp textbox
minBox = fig.add_axes([.01,.6, .05,.075])
minTempBox = TextBox(minBox,"")
#defining max temp textbox
maxBox = fig.add_axes([.01, .4, .05, .075])
maxTempBox = TextBox(maxBox, "")

#defining phone number textbox
phoneBox = fig.add_axes([.9, .5, .1, .075])
phone_number_box = TextBox(phoneBox, "")

#defining labels
minLabel = fig.add_axes([.01, .7, .07, .02])
min_box_label = TextBox(minLabel, "")
min_box_label.set_val("Set Min Temp")

maxLabel = fig.add_axes([.01, .5, .07, .02])
max_box_label = TextBox(maxLabel, "")
max_box_label.set_val("Set Max Temp")

phoneLabel = fig.add_axes([.91, .6, .08, .02])
phone_box_label = TextBox(phoneLabel, "")
phone_box_label.set_val("Enter Phone #")



#defining change box3 display buttons
axes1 = plt.axes([0.7, 0.000001, 0.1, 0.075])
showDisplay_button = Button(axes1, "Show Temperature", color = "blue")
showDisplay_button.on_clicked(on_click1)
plt.connect('button_press_event', on_click1)

#defining radiobuttons
rax = plt.axes([.9, .35, .15, .15])
carrier_choice = RadioButtons(rax, ('AT&T', 'T-Mobile', 'Verizon'))
carrier_choice.on_clicked(change_carriers)

#defining change labelbutton
axes = plt.axes([0.81, 0.000001, 0.1, 0.075])
temp_labelbutton = Button(axes, "change units", color = "blue")
temp_labelbutton.on_clicked(on_click)
#plt.connect('button_press_event', on_click)

send_min_text = True
send_max_text = True
while True:
    last_time = Time[Time.size - 1]
    last_set_min = minTempBox.text
    last_set_max = maxTempBox.text

    fig.canvas.draw()
    fig.canvas.flush_events()
    sleep(2.5)
    a, Time = get_stored_temperatures(db)
    if Time[Time.size-1] == last_time:
        #display error message
        print("error message")

    #should convert array to float
    temp = np.array([])

    for i in a:
        if i == 'nil':
            temp = np.append(temp, None)
        else:
            temp = np.append(temp,float(i))

    if temp.size == 301:
        temp = np.delete(temp, 0)

    temp = np.flip(temp)

    #real time temperature display
    if temp[0] == None:
        txtBox.set_val("Temperature Sensor Unplugged")
        txtBox.stop_typing()
    elif Time[Time.size-1] == last_time: 
        txtBox.set_val("No Data Available")
        txtBox.stop_typing()
    elif ("Temperature in C" in ax.get_ylabel()):
        txtBox.set_val(str(temp[0]) + " Degrees C")
        txtBox.stop_typing()
    else:
        txtBox.set_val(str(temp[0]) + " Degrees F")
        txtBox.stop_typing()
        temp = [a * (9./5) + 32 if a != None else a for a in temp]
        fig.canvas.draw()
        fig.canvas.flush_events()

    #checking min and max temps
    if maxTempBox.text != "":
        if minTempBox.text != "":
            print("testing box entries")
    print("current temp is" + str(temp[0]))

    line1.remove()
    line1, = ax.plot(x,temp, 'b-')

    #checking to see if text has already been sent 
    #will reset once temperature has gone back below or above min/max
    if temp[0] != None:
        if (minTempBox.text != '') and (temp[0] > float(minTempBox.text)):
            send_min_text = True
        if (maxTempBox.text != '') and temp[0] < float(maxTempBox.text):
            send_max_text = True

    #sending text if temperature outside bounds
    if (minTempBox.text != '') and (len(phone_number_box.text) == 10):
        if (send_min_text == True) or (minTempBox.text != last_set_min):
            if (temp[0] != None) and (temp[0] < float(minTempBox.text)):    
                send_sms(phone_number_box.text + attcarrier, "Temperature below " + minTempBox.text + "\n Current Temperature is " + str(temp[0]))
                send_sms(phone_number_box.text + vercarrier, "Temperature below " + minTempBox.text + "\n Current Temperature is " + str(temp[0]))
                send_sms(phone_number_box.text + tmobcarrier, "Temperature below " + minTempBox.text + "\n Current Temperature is " + str(temp[0]))
                send_sms(phone_number_box.text + uscarrier, "Temperature below " + minTempBox.text + "\n Current Temperature is " + str(temp[0]))
                send_min_text = False
    if (maxTempBox.text != '') and (len(phone_number_box.text) == 10):
        if (send_max_text == True) or(maxTempBox.text != last_set_max):
            if (temp[0] != None) and (temp[0] > float(maxTempBox.text)):
                send_sms(phone_number_box.text + attcarrier, "Temperature above " + maxTempBox.text + "\n Current Temperature is " + str(temp[0]))
                send_sms(phone_number_box.text + vercarrier, "Temperature below " + minTempBox.text + "\n Current Temperature is " + str(temp[0]))
                send_sms(phone_number_box.text + tmobcarrier, "Temperature below " + minTempBox.text + "\n Current Temperature is " + str(temp[0]))
                send_sms(phone_number_box.text + uscarrier, "Temperature below " + minTempBox.text + "\n Current Temperature is " + str(temp[0]))
                send_max_text = False
