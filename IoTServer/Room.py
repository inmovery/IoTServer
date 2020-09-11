class Room():
	def __init__(self, id, type_name, length, width, height, home_id):
		self.id = id # int
		self.type_name = type_name # string
		self.length = length # decimal
		self.width = width # decimal
		self.height = height # decimal
		self.home_id = home_id # int

	def getId(self):
		return self.id

	def getTypeName(self):
		return self.type_name

	def getLength(self):
		return self.length

	def getWidth(self):
		return self.width

	def getHeight(self):
		return self.height

	def getHomeId(self):
		return self.home_id
