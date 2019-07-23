from lib.lrandom import get_urandom_bytes
from os import path, remove as os_remove

def file_read_generator(file, bytes_to_read):
	file_read = file.read

	while True:
		data = file_read(bytes_to_read)

		if not data:
			break

		yield data


def get_file_size_zfill(file_path, nfill, getsize=path.getsize):
	return str(getsize(file_path))\
		.zfill(nfill)


def secure_delete(file_path, rounds=10, getsize=path.getsize):
	file_size = getsize(file_path)

	with open(file_path, 'wb') as file:
		file_seek = file.seek
		file_write = file.write

		for i in range(rounds):
			file_seek(0)
			file_write(get_urandom_bytes(file_size))

	os_remove(file_path)
