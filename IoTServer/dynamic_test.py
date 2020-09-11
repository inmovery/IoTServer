# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
# from flask import Flask, jsonify, request, Response
# from flask_restful import reqparse, abort, Api, Resource
# import paho.mqtt.client as mqtt
# import time
# import datetime
# import pymysql
# import json
# import config
# from Sensor import *
# from DbHelper import *
# from threading import Thread
# import feather
# import os
# import pandas as pd
# import py_compile

# def create_new_method(name, sensor):
# 	with open(path + "SchedulerConfig.py", "a+") as file:
# 	    template = """
# def """ + name + """():
# 	file_name = path + "devices/""" + sensor.getFilename() + """.ftr"
# 	dataframe = pd.read_feather(file_name, columns=None, use_threads=True)
# 	value = float(dataframe.loc[0])
# 	payload = CreatePayload(sensor, value)
# 	UpdateDataframe(dataframe, file_name)
# 	client.publish(sensor.getTopic(), payload, QOS, retain)
# 		    """
# 	    file.write(template)
# 	    file.close()
#     # Скомпилим то, что добавили
# 	py_compile.compile(path + 'SchedulerConfig.py')

# db = DbHelper()
# sensors = db.GetListSensors()
# for sensor in sensors:
# 	method_name = sensor.getFilename() + "_" + str(sensor.getId())
# 	create_new_method(method_name, sensor)

# from SchedulerConfig import *