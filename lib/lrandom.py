from os import urandom
from base64 import b64encode

def dev_random(r_bytes):
	with open('/dev/random', 'rb') as file:
		return file.read(r_bytes)


def get_random_bytes(r_bytes):
	return dev_random(r_bytes)


def get_urandom_bytes(ur_bytes):
	return urandom(ur_bytes)


def get_random_pass(l):
	r_divisor = 2
	enough_entropy_chars = 33

	_l = l/1.3
	r_l = int(_l / r_divisor) or 1

	if r_l > enough_entropy_chars:
		increment_reducer = 10
		r_l = int(enough_entropy_chars + r_l / increment_reducer)

	ur_l = int(_l - r_l)

	r_bytes = get_random_bytes(r_l)
	ur_bytes = get_urandom_bytes(ur_l)

	return b64encode(r_bytes + ur_bytes)[:l].decode()


def get_random_pin(l):
	r_pass = get_random_pass(int(l/2))
	r_pin = ''

	counter = 0
	_sum = 1

	while len(r_pin) < l:
		r_pin += str(ord(r_pass[counter]))
		counter += _sum

	return r_pin[:l]