import config
import pymysql
from Sensor import *
from SensorType import *
from Room import *
from RoomType import *

class DbHelper():
	def __init__(self):
		self.con = pymysql.connect(config.DB_HOST, config.DB_USERNAME, config.DB_PASSWORD, config.DB_NAME)

	# Получение информации о всех датчиках
	def GetListSensors(self):
		sensors = []
		with self.con:
			cursor = self.con.cursor()
			query_sensors = "SELECT * FROM sensors"
			cursor.execute(query_sensors)
			
			result = ""
			for sensor in cursor.fetchall():
				sensor_id = sensor[0]
				frequency = sensor[8]
				is_active = sensor[9]
				topic = sensor[5]
				name = sensor[1]
				description = sensor[2]
				
				# get location
				room_id = sensor[4]
				room_name_query = "SELECT room_types.RoomName, rooms.Length, rooms.Width, rooms.Height, rooms.HomeId FROM rooms, room_types WHERE rooms.RoomType = room_types.RoomTypeId AND rooms.RoomId = %s"
				query_params = (room_id)
				cursor.execute(room_name_query, query_params)
				room_info = cursor.fetchone()
				room_name = room_info[0]
				room_length = float(room_info[1])
				room_width = float(room_info[2])
				room_height = float(room_info[3])
				room_home_id = room_info[4]

				room = Room(room_id, room_name, room_length, room_width, room_height, room_home_id)

				# get sensor_type
				sensor_type_id = sensor[3]
				sensor_type_query = "SELECT SensorTypeName, isActuator FROM sensor_types WHERE SensorTypeId = %s"
				query_params = (sensor_type_id)
				cursor.execute(sensor_type_query, query_params)
				result_query = cursor.fetchone()
				
				sensor_type = SensorType(sensor_type_id, result_query[0], result_query[1])
				
				url_image = sensor[6]
				url_csv = sensor[7] 

				temp_sensor = Sensor(sensor_id, topic, name, description, room, sensor_type, url_csv, frequency, is_active, url_image)
				sensors.append(temp_sensor)

		return sensors
	
	# Получение информации о датчике по ID
	def GetSensorById(self, id):
		sensors = []
		with self.con:
			cursor = self.con.cursor()
			query = "SELECT * FROM sensors WHERE SensorId = %s"
			query_params = (id)
			cursor.execute(query, query_params)
			
			sensor = cursor.fetchall()[0]
			
			sensor_id = sensor[0]
			frequency = sensor[8]
			is_active = sensor[9]
			topic = sensor[5]
			name = sensor[1]
			description = sensor[2]
				
			# get location
			room_id = sensor[4]
			room_name_query = "SELECT room_types.RoomName, rooms.Length, rooms.Width, rooms.Height, rooms.HomeId FROM rooms, room_types WHERE rooms.RoomType = room_types.RoomTypeId AND rooms.RoomId = %s"
			query_params = (room_id)
			cursor.execute(room_name_query, query_params)
			room_info = cursor.fetchone()
			room_name = room_info[0]
			room_length = float(room_info[1])
			room_width = float(room_info[2])
			room_height = float(room_info[3])
			room_home_id = room_info[4]

			room = Room(room_id, room_name, room_length, room_width, room_height, room_home_id)

			# get sensor_type
			sensor_type_id = sensor[3]
			sensor_type_query = "SELECT SensorTypeName, isActuator FROM sensor_types WHERE SensorTypeId = %s"
			query_params = (sensor_type_id)
			cursor.execute(sensor_type_query, query_params)
			result_query = cursor.fetchone()
				
			sensor_type = SensorType(sensor_type_id, result_query[0], result_query[1])
				
			url_image = sensor[6]
			url_csv = sensor[7] 

			response = Sensor(sensor_id, topic, name, description, room, sensor_type, url_csv, frequency, is_active, url_image)

		return response

	# Активация датчика
	def EnableSensor(self, id):
		cursor = self.con.cursor()

		query = "UPDATE sensors SET isActive = 1 WHERE SensorId = %s"
		query_params = (id)
		cursor.execute(query, query_params)

		self.con.commit()

	# Деактивация датчика
	def DisableSensor(self, id):
		cursor = self.con.cursor()

		query = "UPDATE sensors SET isActive = 0 WHERE SensorId = %s"
		query_params = (id)
		cursor.execute(query, query_params)

		self.con.commit()

	# Удаление датчика
	def DeleteSensor(self, id):
		cursor = self.con.cursor()

		query = "DELETE FROM sensors WHERE SensorId = %s"
		query_params = (id)
		cursor.execute(query, query_params)

		self.con.commit()

	# Получение всех комнат
	def GetListRooms(self):
		rooms = []
		with self.con:
			cursor = self.con.cursor()
			# Запрос на полчение информации обо всех комнатах
			query_rooms = "SELECT * FROM rooms"
			cursor.execute(query_rooms)
			
			for room in cursor.fetchall():
				room_id = room[0] # ID комнаты

				# Получение типа комнаты
				room_type_query = "SELECT RoomName FROM room_types WHERE RoomTypeId = %s"
				room_type_id = room[1]
				query_params = (room_type_id)  
				cursor.execute(room_type_query, query_params)
				room_type = cursor.fetchone()[0]

				room_length = float(room[2]) # Длина комнаты
				room_width = float(room[3]) # Ширина комнаты
				room_height = float(room[4]) # Высота комнаты

				home_id = room[5] # ID дома, которому принадлежит комната

				temp_room = Room(room_id, room_type, room_length, room_width, room_height, home_id)
				rooms.append(temp_room)

		return rooms

	# Получение информации о комнате по ID
	def GetRoomById(self, id):
		with self.con:
			cursor = self.con.cursor()
			# Запрос на полчение информации обо всех комнатах
			query_sensors = "SELECT * FROM rooms WHERE RoomId = %s"
			query_params = (id)
			cursor.execute(query_sensors, query_params)
			
			room = cursor.fetchall()[0]

			room_id = room[0] # ID комнаты

			# Получение типа комнаты
			room_type_query = "SELECT RoomName FROM room_types WHERE RoomTypeId = %s"
			room_type_id = room[1]
			query_params = (room_type_id)
			cursor.execute(room_type_query, query_params)
			room_type = cursor.fetchone()[0]

			room_length = float(room[2]) # Длина комнаты
			room_width = float(room[3]) # Ширина комнаты
			room_height = float(room[4]) # Высота комнаты

			home_id = room[5] # ID дома, которому принадлежит комната

			response = Room(room_id, room_type, room_length, room_width, room_height, home_id)
		
		return response

	# Удаление комнаты (добавить учёт FK)
	def DeleteRoom(self, id):
		cursor = self.con.cursor()

		query = "DELETE FROM rooms WHERE RoomId = %s"
		query_params = (id)
		cursor.execute(query, query_params)

		self.con.commit()

	# Получение всех комнат
	def GetListRoomTypes(self):
		room_types = []
		with self.con:
			cursor = self.con.cursor()
			# Запрос на полчение информации обо всех комнатах
			query_room_types = "SELECT * FROM room_types"
			cursor.execute(query_room_types)
			
			for room_type in cursor.fetchall():
				type_id = room_type[0] # ID типа комнаты
				type_name = room_type[1] # Название типа комнаты
				
				temp_room_type = RoomType(type_id, type_name)
				room_types.append(temp_room_type)

		return room_types

	# Получение информации о типе комнаты по ID
	def GetRoomTypeById(self, id):
		with self.con:
			cursor = self.con.cursor()
			# Запрос на полчение информации обо всех комнатах
			query_room_types = "SELECT * FROM room_types WHERE RoomTypeId = %s"
			query_params = (id)
			cursor.execute(query_room_types, query_params)
			
			room_type = cursor.fetchall()[0]

			type_id = room_type[0] # ID типа комнаты
			type_name = room_type[1] # Название типа комнаты
			
			response = RoomType(type_id, type_name)
			
		return response

	# Удаление типа комнаты (добавить учёт FK)
	def DeleteRoomType(self, id):
		cursor = self.con.cursor()

		query = "DELETE FROM room_types WHERE RoomTypeId = %s"
		query_params = (id)
		cursor.execute(query, query_params)

		self.con.commit()

	# Получение всех типов датчиков
	def GetListSensorTypes(self):
		sensor_types = []
		with self.con:
			cursor = self.con.cursor()
			# Запрос на получение данных обо всех типах датчиков
			query_rooms = "SELECT * FROM sensor_types"
			cursor.execute(query_rooms)
			
			for sensor_type in cursor.fetchall():
				type_id = sensor_type[0] # ID типа комнаты
				type_name = sensor_type[1] # Название типа комнаты
				is_actuator = sensor_type[2] # Факт того, относится ли тип датчик к числу управляющих устройств

				temp_sensor_type = SensorType(type_id, type_name, is_actuator)
				sensor_types.append(temp_sensor_type)

		return sensor_types

	# Получение информации о типе датчика по ID
	def GetSensorTypeById(self, id):
		with self.con:
			cursor = self.con.cursor()
			# Запрос на полчение информации обо всех комнатах
			query_sensor_types = "SELECT * FROM sensor_types WHERE SensorTypeId = %s"
			query_params = (id)
			cursor.execute(query_sensor_types, query_params)
			
			sensor_type = cursor.fetchall()[0]

			type_id = sensor_type[0] # ID типа комнаты
			type_name = sensor_type[1] # Название типа комнаты
			is_actuator = sensor_type[2] # Факт того, относится ли тип датчик к числу управляющих устройств
			
			response = SensorType(type_id, type_name, is_actuator)
			
		return response

	# Удаление типа комнаты (добавить учёт FK)
	def DeleteSensorType(self, id):
		cursor = self.con.cursor()

		query = "DELETE FROM sensor_types WHERE SensorTypeId = %s"
		query_params = (id)
		cursor.execute(query, query_params)

		self.con.commit()


