class Sensor():
	def __init__(self, id, topic, name, description, room, sensor_type, url_csv,
		frequency, is_active, url_image):
		self.id = id # int
		self.topic = topic # string
		self.name = name # string
		self.description = description # string
		self.room = room # Room object
		self.sensor_type = sensor_type # SensorType object
		self.frequency = frequency # int
		self.is_active = is_active # boolean
		self.url_csv = url_csv # string (this is path to csv source)
		self.url_image = url_image # string
	
	def getId(self):
		return self.id

	def getTopic(self):
		return self.topic

	def getName(self):
		return self.name

	def getDescription(self):
		return self.description

	def getRoom(self):
		return self.room

	def getSensorType(self):
		return self.sensor_type

	def getUrlCsv(self):
		return self.url_csv

	def getIsActive(self):
		return self.is_active

	def getFrequency(self):
		return self.frequency

	def getUrlImage(self):
		return self.url_image

