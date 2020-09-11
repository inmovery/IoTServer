from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from flask import Flask, jsonify, request, Response
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
import paho.mqtt.client as mqtt
import time
import datetime
import pymysql
import json
import config
from Sensor import *
from DbHelper import *
from threading import Thread
import feather
import os
import pandas as pd
import py_compile

path = os.getcwd() + "/IoTServer/"

# QOS = 0
# retain = False
# uuid = config.MQTT_UUID

# client = mqtt.Client(client_id=uuid)
# exitFlag = True # для аутентификации

# user = config.MQTT_USER
# password = config.MQTT_PASSWORD

# client.username_pw_set(username=user, password=password)

# ========================Call Backs==========================================================================

# Событие публикации
# def on_publish(client, userdata, mid):
#     my_file = open("publications.txt", 'a')
#     my_file.write("Publish " + str(mid) + "\n")
#     my_file.close()

# # Событие подключения к брокеру
# def on_connect(pvtClient, userdata, flags, rc):
#     global exitFlag
#     if(rc == 0): # Если соединение прошла успешно
#         my_file = open("connections.txt", 'a')
#         my_file.write("Connected to client! Return Code: " + str(rc) + "\n")
#         my_file.close()
#         exitFlag = False
#     elif (rc == 5):  # Если произошла ошибка аутентификации
#         my_file = open("connections.txt", 'a')
#         my_file.write("Authentication Error! Return Code: " + str(rc) + "\n")
#         my_file.close()
#         client.disconnect()
#         exitFlag = True

# # Логирование
# def on_log(client, userdata, level, buf):
#     # Будут логироваться флаги , которые будут использоваться Publisher и Subscriber
#     my_file = open("flags.txt", 'a')
#     my_file.write(str(buf) + "\n")
#     my_file.close()

# # Отключение от брокера
# def on_disconnect(pvtClient, userdata, rc): # Запустится, когда будет вызван метод disconnect()
#     my_file = open("connections.txt", 'a')
#     my_file.write("Disconnection. Disconnecting reason is " + str(rc) + "\n")
#     my_file.close()
#     client.disconnect()

# Создание сообщения, которое якобы будет отправлять датчик
def CreatePayload(sensor, value):
	topic = sensor.getTopic()
	name = sensor.getName()
	mac_address = "" # Тут нужно срандомить
	location = sensor.getLocation()
	value = value # 1/0 or float value
	time = datetime.datetime.now().strftime("%d.%m %H:%M:%S") # UTC (end with "Z")
	is_actuator = sensor.getIsActuator()
	sensor_type = sensor.getSensorType()
	json_pre = {
		"Topic": topic,
		"Name": name,
		"MAC Address": mac_address,
		"Location": location,
		"SensorType": sensor_type,
		"IsActuator": is_actuator,
		"Value": value,
		"Time": time
	}
	json_result = json.dumps(json_pre, ensure_ascii=False)
	return json_result

# Обновление сгенерированного файла датчика
def UpdateDataframe(dataframe, filename):
	# Удаляем первое значение
	dataframe_upd = dataframe.drop(0)
	# Обновляем индексы
	dataframe_upd.reset_index(drop=True, inplace=True)

	dataframe_upd.to_feather(filename)

# Генерация идентификатор потока датчика
def GenerateJobId(sensor):
	job_id = sensor.getUrlCsv() + "_" + str(sensor.getId())
	return job_id

# Обработка какого-либо датчика
def PerformSensor(sensor):
	# Идентификатор потока датчика
	job_id = GenerateJobId(sensor)

	# Путь к файлу, сгенерированному на основе загруженного CSV файла
	file_name = path + "devices/" + job_id + ".ftr"

	# Читаем соответствующий датчику сгенерированный файл
	dataframe = pd.read_feather(file_name, columns=None, use_threads=True)
	value = float(dataframe.loc[0])

	# Тут место для прогнозирования временного ряда

	# Создаём сообщение, которое якобы будет отправлять датчик/управляющее усройство
	payload = CreatePayload(sensor, value)

	# Отправляем сообщение со стороны датчика
	# client.publish(sensor.getTopic(), payload, QOS, retain)

	# Обновляем сгенерированный файл датчика для того, чтобы продвинуть "монитор временного ряда"
	UpdateDataframe(dataframe, file_name)

# Создание и активация работы (потока для датчика)
def CreateJob(scheduler, sensor, interval):
	job_id = GenerateJobId(sensor)
	scheduler.add_job(lambda: PerformSensor(sensor), 'interval', seconds=interval, name=job_id, id=job_id)

# Инициализация библиотеки APScheduler
scheduler = BackgroundScheduler({'apscheduler.timezone': 'UTC'})

# Инициализация БД (MySQL)
db = DbHelper()

# client.on_publish = on_publish
# client.on_connect = on_connect
# client.on_log = on_log
# client.on_disconnect = on_disconnect

# broker_address = "soldier.cloudmqtt.com"
# port = 17777
# keepAlive = 60

# client.connect(broker_address, port, keepAlive)

# client.loop_start()
scheduler.start()
# client.loop_stop()

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# parser = reqparse.RequestParser()

# parser.add_argument('sensor_id', type=int)
# parser.add_argument('sensor_name', type=str)
# parser.add_argument('sensor_location', type=str) # может быть числом, но юзер выбирает строку из списка, а не число
# parser.add_argument('sensor_type', type=str) # может быть числом, но пользователь выбирает строку
# parser.add_argument('topic', type=str)
# parser.add_argument('sensor_description', type=str)
# parser.add_argument('url_image', type=str) # тут ссылка на какой-то ресурс с картинкой
# parser.add_argument('url_csv', type=str) # тут ссылка на csv файл, залитый куда-то (google drive or smath else)
# parser.add_argument('frequency', type=int)
# parser.add_argument('is_actuator', type=int)

# Управление датчиками

@app.route('/')
def iot_server():
	return "Welcome, OL."

# Это удалить
@app.route('/jobs')
def jobs():
	jobs = scheduler.get_jobs()
	output = ""
	for job in jobs:
		output += (job.name + "<br>")
	return output

# Структура запроса:
# 1. Маршрут -> URL адрес (URL address)
# 2. Тип метода (POST, GET, PUT, PATCH, DELETE)
# 3. Заголовки (Headers)
# 4. Данные (Pyload)

# Получение списка всех запущенных работ (потоков)
def getJobsId():
	result = []
	jobs = scheduler.get_jobs()
	for job in jobs:
		result.append(job.name)
	return result

# Получение всех датчиков
class SensorsList(Resource):
	def get(self):
		db = DbHelper()
		sensors = db.GetListSensors()
		results = []
		for sensor in sensors:
			result = {
				"id": sensor.getId(),
				"name": sensor.getName(),
				"topic": sensor.getTopic(),
				"location": {
					"room_id": sensor.getRoom().getId(),
					"type_name": sensor.getRoom().getTypeName(),
					"length": sensor.getRoom().getLength(),
					"width": sensor.getRoom().getWidth(),
					"height": sensor.getRoom().getHeight(),
					"home_id": sensor.getRoom().getHomeId()
				},
				"sensor_type": {
					"type_id": sensor.getSensorType().getTypeId(),
					"type_name": sensor.getSensorType().getTypeName(),
					"is_actuator": sensor.getSensorType().getIsActuator()
				},
				"description": sensor.getDescription(),
				"frequency": sensor.getFrequency(),
				"is_active": sensor.getIsActive(),
				"url_image": sensor.getUrlImage(),
				"url_csv": sensor.getUrlCsv()
			}
			results.append(result)
		return [result for result in results], 200

# Активация всех датчиков
class SensorsActivate(Resource):
	def patch(self):
		db = DbHelper()
		sensors = db.GetListSensors()
		for sensor in sensors:
			# Если датчик не активирован
			if(sensor.getIsActive() == 0):
				# Выполнение запроса на активацию всех датчиков
				id_sensor = sensor.getId()
				db.EnableSensor(id_sensor)

				# Создание потока для датчика
				frequency = sensor.getFrequency()
				CreateJob(scheduler, sensor, frequency)
		return { "result": "Operate successfully" }, 200

# Включение датчика
class EnableSensor(Resource):
	def patch(self, id):
		db = DbHelper()
		# Получаем ID всех запущенных работ (потоков датчиков)
		jobs_id = getJobsId()
		
		# Получаем информацию о датчике
		sensor = db.GetSensorById(id)
		
		# Генерируем ID потока данного датчика
		gen_job_id = GenerateJobId(sensor)
		
		# Если датчик уже запущен
		if gen_job_id in jobs_id:
			# то ничего не делаем
			pass
		else:
			# Выполняем запрос на активацию датчика
			db.EnableSensor(id)

			# Создаём поток для датчика
			frequency = sensor.getFrequency()
			CreateJob(scheduler, sensor, frequency)

		sensor = db.GetSensorById(id)

		data = {
			"id": sensor.getId(),
			"name": sensor.getName(),
			"topic": sensor.getTopic(),
			"location": {
				"room_id": sensor.getRoom().getId(),
				"type_name": sensor.getRoom().getTypeName(),
				"length": sensor.getRoom().getLength(),
				"width": sensor.getRoom().getWidth(),
				"height": sensor.getRoom().getHeight(),
				"home_id": sensor.getRoom().getHomeId()
			},
			"sensor_type": {
				"type_id": sensor.getSensorType().getTypeId(),
				"type_name": sensor.getSensorType().getTypeName(),
				"is_actuator": sensor.getSensorType().getIsActuator()
			},
			"description": sensor.getDescription(),
			"frequency": sensor.getFrequency(),
			"is_active": sensor.getIsActive(),
			"url_image": sensor.getUrlImage(),
			"url_csv": sensor.getUrlCsv()
		}

		return { "result": "Operate successfully", "data": data }, 200

# Выключение датчика
class DisableSensor(Resource):
	def patch(self, id):
		db = DbHelper()
		# Получаем ID всех запущенных работ (потоков датчиков)
		jobs_id = getJobsId()
		
		# Получаем информацию о датчике
		sensor = db.GetSensorById(id)
		
		# Генерируем ID потока данного датчика
		gen_job_id = GenerateJobId(sensor)
		
		# Если датчик запущен
		if gen_job_id in jobs_id:
			# Удаляем поток датчика
			scheduler.remove_job(gen_job_id)

			# Выполняем запрос на деактивацию датчика
			db.DisableSensor(id)
		else:
			# иначе ничего не делаем
			pass

		sensor = db.GetSensorById(id)

		data = {
			"id": sensor.getId(),
			"name": sensor.getName(),
			"topic": sensor.getTopic(),
			"location": {
				"room_id": sensor.getRoom().getId(),
				"type_name": sensor.getRoom().getTypeName(),
				"length": sensor.getRoom().getLength(),
				"width": sensor.getRoom().getWidth(),
				"height": sensor.getRoom().getHeight(),
				"home_id": sensor.getRoom().getHomeId()
			},
			"sensor_type": {
				"type_id": sensor.getSensorType().getTypeId(),
				"type_name": sensor.getSensorType().getTypeName(),
				"is_actuator": sensor.getSensorType().getIsActuator()
			},
			"description": sensor.getDescription(),
			"frequency": sensor.getFrequency(),
			"is_active": sensor.getIsActive(),
			"url_image": sensor.getUrlImage(),
			"url_csv": sensor.getUrlCsv()
		}

		return { "result": "Operate successfully", "data": data }, 200

# Получение информации о датчике (GET) + Удаление датчика (DELETE)
class SensorActions(Resource):
	# Получение данных о датчике
	def get(self, id):
		db = DbHelper()
		sensor = db.GetSensorById(id)
		result = {
			"id": sensor.getId(),
			"name": sensor.getName(),
			"topic": sensor.getTopic(),
			"location": {
				"room_id": sensor.getRoom().getId(),
				"type_name": sensor.getRoom().getTypeName(),
				"length": sensor.getRoom().getLength(),
				"width": sensor.getRoom().getWidth(),
				"height": sensor.getRoom().getHeight(),
				"home_id": sensor.getRoom().getHomeId()
			},
			"sensor_type": {
				"type_id": sensor.getSensorType().getTypeId(),
				"type_name": sensor.getSensorType().getTypeName(),
				"is_actuator": sensor.getSensorType().getIsActuator()
			},
			"description": sensor.getDescription(),
			"frequency": sensor.getFrequency(),
			"is_active": sensor.getIsActive(),
			"url_image": sensor.getUrlImage(),
			"url_csv": sensor.getUrlCsv()
		}
		
		return result, 200

	# Удаление датчикка
	def delete(self, id):
		try:
			db.DeleteSensor(id)
			# resource deleted successfully
			return { "result": "Operate successfully"}, 200
		except:
			# resource can't be removed reset to a default
			return { "result": "Operate occured exception due to table relationship"}, 205

# Создание датчика
class CreateSensor(Resource):
	def post(self):
		# data_json = parser.parse_args()
		data_json = request.get_json()

		sensor_name = data_json['sensor_name']
		sensor_location = data_json['sensor_location']
		sensor_type = data_json['sensor_type']
		topic = data_json['topic']
		sensor_description = data_json['sensor_description']
		url_image = data_json['url_image']
		url_csv = data_json['url_csv']
		frequency = data_json['frequency']

		# return {"sensor_name": sensor_name, "sensor_location": sensor_location, "sensor_type": sensor_type,
		# 		"topic": topic, "sensor_description": sensor_description, "url_image": url_image,
		# 		"url_csv": url_csv, "frequency": frequency}, 200
		return data_json, 200

# Получение информации обо всех комнатах
class RoomsList(Resource):
	def get(self):
		db = DbHelper()
		rooms = db.GetListRooms()
		results = []
		for room in rooms:
			result = {
				"id": room.getId(),
				"type_name": room.getTypeName(),
				"length": room.getLength(),
				"width": room.getWidth(),
				"height": room.getHeight(),
				"home_id": room.getHomeId()
			}
			results.append(result)
		return [result for result in results], 200

# Получение / Удаление комнаты
class RoomActions(Resource):
	# Получение данных о комнате
	def get(self, id):
		db = DbHelper()
		room = db.GetRoomById(id)
		result = {
			"id": room.getId(),
			"type_name": room.getTypeName(),
			"length": room.getLength(),
			"width": room.getWidth(),
			"height": room.getHeight(),
			"home_id": room.getHomeId()
		}
		
		return result, 200

	# Удаление комнаты
	def delete(self, id):
		db = DbHelper()
		try:
			db.DeleteRoom(id)
			# resource deleted successfully
			return { "result": "Operate successfully"}, 200
		except:
			# resource can't be removed reset to a default
			return { "result": "Operate occured exception due to table relationship"}, 205

# Создание комнаты
class CreateRoom(Resource):
	def post(self):
		# data_json = parser.parse_args()
		data_json = request.get_json()

		room_type_id = data_json['room_type_id']
		room_type_name = data_json['room_type_name']

		room_length = data_json['room_length']
		room_width = data_json['room_width']
		room_height = data_json['room_height']

		# return {"room_type_name": room_type_name, "room_length": room_length,
		# 		"room_width": room_width, "room_height": room_height}, 200
		return data_json, 200

# Получение информации обо всех типах комнат
class RoomTypesList(Resource):
	def get(self):
		db = DbHelper()
		room_types = db.GetListRoomTypes()
		results = []
		for room_type in room_types:
			result = {
				"id": room_type.getTypeId(),
				"type_name": room_type.getTypeName()
			}
			results.append(result)
		return [result for result in results], 200

# Получение / Удаление комнаты
class RoomTypesActions(Resource):
	# Получение данных о типе комнаты
	def get(self, id):
		db = DbHelper()
		room_type = db.GetRoomTypeById(id)
		result = {
			"id": room_type.getTypeId(),
			"type_name": room_type.getTypeName()
		}
		
		return result, 200

	# Удаление типа комнаты
	def delete(self, id):
		db = DbHelper()
		try:
			db.DeleteRoomType(id)
			# resource deleted successfully
			return { "result": "Operate successfully"}, 200
		except:
			# resource can't be removed reset to a default
			return { "result": "Operate occured exception due to table relationship"}, 205

# Создание типа комнаты
class CreateRoomType(Resource):
	def post(self):
		# data_json = parser.parse_args()
		data_json = request.get_json()
		
		room_type_name = data_json['room_type_name']
		
		# return {"room_name": room_type_name}, 200
		return data_json, 200

# Получение информации обо всех типах датчиков
class SensorTypesList(Resource):
	def get(self):
		db = DbHelper()
		sensor_types = db.GetListSensorTypes()
		results = []
		for sensor_type in sensor_types:
			result = {
				"id": sensor_type.getTypeId(),
				"type_name": sensor_type.getTypeName(),
				"is_actuator": sensor_type.getIsActuator()
			}
			results.append(result)
		return [result for result in results], 200

# Получение / Удаление типа датчика
class SensorTypesActions(Resource):

	# Получение данных о типе датчика
	def get(self, id):
		db = DbHelper()
		sensor_type = db.GetSensorTypeById(id)
		result = {
			"id": sensor_type.getTypeId(),
				"type_name": sensor_type.getTypeName(),
				"is_actuator": sensor_type.getIsActuator()
		}
		
		return result, 200

	# Удаление типа датчика
	def delete(self, id):
		db = DbHelper()
		try:
			db.DeleteSensorType(id)
			# resource deleted successfully
			return { "result": "Operate successfully"}, 200
		except:
			# resource can't be removed reset to a default
			return { "result": "Operate occured exception due to table relationship"}, 205

# Создание типа датчика
class CreateSensorType(Resource):
	def post(self):
		# data_json = parser.parse_args()
		data_json = request.get_json()
		
		sensor_type_name = data_json['sensor_type_name']
		is_actuator = data_json['is_actuator']
		
		# return {"sensor_type_name": sensor_type_name, "is_actuator": is_actuator}, 200
		return data_json, 200

# =======================
# Работа с датчиками (+-)
# =======================

# Получение всех датчиков (GET)
api.add_resource(SensorsList, '/api/sensors')

# Активация всех датчиков (PATCH) — нициализация датчиков
api.add_resource(SensorsActivate, '/api/sensors/activate')

# Включение датчика (PATCH) - не менять
api.add_resource(EnableSensor, '/api/sensor/enable/<int:id>')

# Выключение датчиков датчика (PATCH) - не менять
api.add_resource(DisableSensor, '/api/sensor/disable/<int:id>')

# Получение данных о датчике (GET) + Удаление датчика (DELETE)
api.add_resource(SensorActions, '/api/sensors/<int:id>')

# Создание нового датчика (POST)
api.add_resource(CreateSensor, '/api/sensors/create')

# Редактирование датчика (PUT)
# api.add_resource(EditSensor, '/api/sensors/<int:room_id>/edit')

# ======================
# Работа с комнатами (+)
# ======================

# Получение информации обо всех комнатах (GET)
api.add_resource(RoomsList, '/api/rooms')

# Получение данных о комнате (GET) + Удаление комнаты (DELETE)
api.add_resource(RoomActions, '/api/rooms/<int:id>')

# Создание нового датчика (POST)
api.add_resource(CreateRoom, '/api/rooms/create')

# Редактирование датчика (PUT)
# api.add_resource(EditRoom, '/api/rooms/<int:room_id>/edit')

# ==========================
# Работа с типами комнат (+)
# ==========================

# Получение информации обо всех типах комнат (GET)
api.add_resource(RoomTypesList, '/api/rooms/types')

# Получение данных о типе комнаты (GET) + Удаление типа комнаты (DELETE)
api.add_resource(RoomTypesActions, '/api/rooms/types/<int:id>')

# Создание нового датчика (POST)
api.add_resource(CreateSensorType, '/api/sensors/types/create')

# Редактирование датчика (PUT)
# api.add_resource(EditSensorType, '/api/sensors/types/<int:room_id>/edit')

# ============================
# Работа с типами датчиков (+)
# ============================

# Получение информации обо всех типах датчиков (GET)
api.add_resource(SensorTypesList, '/api/sensors/types')

# Получение данных о типе датчика (GET) + Удаление типа датчика (DELETE)
api.add_resource(SensorTypesActions, '/api/sensors/types/<int:id>')

# Создание нового датчика (POST)
api.add_resource(CreateRoomType, '/api/rooms/types/create')

# Редактирование датчика (PUT)
# api.add_resource(EditRoomType, '/api/rooms/types/<int:room_id>/edit')

# Работа с MQTT брокером

# Работа с возможными действиями датчиков

if __name__ == '__main__':
	app.run()

# TODO: 
# 	* Настроить REST архитуктуру на редактирование запущенных сценариев
# 	* Спросить ОЛ про то, нужны ли пользователи и отдельно ли должно быть написано ТЗ или их как-то вставить в приложения
# 	* Добавить refresh jobs (refresh threads)
