from DbHelper import *
from Sensor import *
import pandas as pd
import feather
import json
import time
import datetime
import os

path = os.getcwd() + "/IoTServer/"

def create_payload(sensor, value):
	topic = sensor.getTopic()
	name = sensor.getName()
	mac_address = "" # Тут нужно срандомить
	location = sensor.getLocation()
	value = value
	time = datetime.datetime.now().strftime("%d.%m %H:%M:%S")
	is_actuator = sensor.getIsActuator()
	sensor_type = sensor.getSensorType()
	json_pre = {"Topic": topic, 
				"Name": name, 
				"MAC Address": mac_address, 
				"Location": location, 
				"SensorType": sensor_type, 
				"IsActuator": is_actuator, 
				"Value": value, 
				"Time": time}
	json_result = json.dumps(json_pre, ensure_ascii=False)
	return json_result

def update_dataframe(dataframe, filename):
	# Удаляем первое значение
	dataframe_upd = dataframe.drop(0)
	# Обновляем индексы
	dataframe_upd.reset_index(drop=True, inplace=True)
	dataframe_upd.to_feather(filename)
		    