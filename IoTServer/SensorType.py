class SensorType():
	def __init__(self, type_id, type_name, is_actuator):
		self.type_id = type_id # int
		self.type_name = type_name # string
		self.is_actuator = is_actuator # boolean

	def getTypeId(self):
		return self.type_id

	def getTypeName(self):
		return self.type_name

	def getIsActuator(self):
		return self.is_actuator