import pyrebase
from collections import OrderedDict
import numpy as np
import time

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://ece-4880-lab1-default-rtdb.firebaseio.com/",
  "storageBucket": "projectId.appspot.com"
}

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

def push_temperature(db, temp):
    db.child("Temperature").push(temp)

    current_time = time.strftime("%H:%M:%S", time.localtime())
    db.child("Time").push(current_time)

    temp_data, time_data = db.child("Temperature").get().val(), db.child("Time").get().val()

    if len(temp_data) > 300:
        fixed_temp_data = OrderedDict(list(temp_data.items())[len(temp_data)-300:])
        db.child("Temperature").set(fixed_temp_data)

    if len(time_data) > 300:
        fixed_time_data = OrderedDict(list(time_data.items())[len(time_data)-300:])
        db.child("Time").set(fixed_time_data)

def get_read_temperature_button(db):
    return db.child("ReadTemperatureButton").get().val()

def set_read_temperature_button(db, state):
    if state != 0 and state != 1:
        return
    
    db.child("ReadTemperatureButton").set(state)

def get_physical_switch_state(db):
    return db.child("PhysicalSwitch").get().val()

def set_physical_switch_state(db, state):
    if state != 0 and state != 1:
        return

    db.child("PhysicalSwitch").set(state)

if __name__ == "__main__":
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    print(get_physical_switch_state(db))
    