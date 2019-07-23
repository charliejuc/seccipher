def get_by_index(index, arr):
	try:
		return arr[index]
	except IndexError:
		return None