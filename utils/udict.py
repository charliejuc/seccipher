from collections import OrderedDict

class OrderedDictExtended(OrderedDict):
	first_key = None
	last_key = None
	has_values = False
	awni = list()

	def __setitem__(self, key, value):
		if not self.has_values:
			self.has_values = bool(self)

		super(OrderedDictExtended, self).__setitem__(key, value)

		self.insert_refresh(key, value)

	def __delitem__(self, key):
		super(OrderedDictExtended, self).__delitem__(key)

		self.has_values = bool(self)

		self.delete_refresh(key)

	def insert_refresh(self, inserted_key, value):
		if not self.has_values:
			self.first_key = inserted_key

		self.last_key = inserted_key

		if self.awni and isinstance(inserted_key, int):
			self.awni.append(value)

	def delete_refresh(self, deleted_key):
		if self.awni and isinstance(deleted_key, int):
			self.awni = self.get_awni(force=True)

		if not self.has_values:
			self.first_key = None
			self.last_key = None
			return

		if deleted_key == self.first_key:
			self.first_key = next(self.keys())
			return

		if deleted_key == self.last_key:
			self.last_key = next(reversed(self.keys()))
			return

	def get_array_with_numeric_indexes(self, force=False):
		if not force and self.awni:
			return self.awni

		self.awni = [ value for key, value in self.items() if isinstance(key, int) ]

		return self.awni

	def get_awni(self, *args, **kwargs):
		return self.get_array_with_numeric_indexes(*args, **kwargs)

	def first(self):
		return self.__getitem__(self.first_key)
	
	def last(self):
		return self.__getitem__(self.last_key)