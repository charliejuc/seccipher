from hashlib import sha256, sha512
from time import time
from functools import reduce

hash_algo = sha512

rounds = 50
row_id_rounds_reduction = 5
row_id_rounds = int(rounds / row_id_rounds_reduction)

def hash_algo_rounds(value, rounds):
	hash_algo_obj = hash_algo(value)
	rounds -= 1

	while rounds:
		hash_algo_obj = hash_algo(hash_algo_obj.digest())

		rounds -= 1

	return hash_algo_obj


def get_row_id():
	return sha256(
			hash_algo_rounds(
				str(time()).encode('utf-8'),
				rounds=row_id_rounds
			).digest()
		).hexdigest()


def get_hash_digest(value, rounds=rounds):
	return hash_algo_rounds(
		value.encode('utf-8'),
		rounds=rounds
	).digest()


def get_rounds(key, min_rounds=5, max_rounds=60, mult=15, reducer=2):
	key_len = len(key)
	ords = [ ord(c) for c in key ]

	r_ords = reduce(lambda x, y: x + y, ords)

	rounds = min_rounds + mult * r_ords / (key_len**reducer)
	rounds -= rounds / 2

	if rounds <= max_rounds:
		return int(rounds)

	return int(max_rounds - rounds / max_rounds)