from Crypto.Cipher import AES, Blowfish
from lib.lhash import get_hash_digest, get_rounds
from lib.lrandom import get_random_bytes
from utils.ucrypto import get_encrypt_file_path, get_decrypt_file_path, get_intermediate_file_path, intermediate_file_ext
from utils.ufile import file_read_generator, get_file_size_zfill, secure_delete
import os, shutil

chunk_size = 64 * 1000 #bytes
hash_bytes_half = 32
cipher_algos = [ AES, Blowfish, ]
file_rounds_bytes = 8

def remove_intermediate_files(directory):
	for file in os.listdir(directory):
		if file.endswith(intermediate_file_ext):
			os.remove(file)

def decrypt(raw_key, file_path, rounds=1, output_file_path=None, to_mem=False, *args, **kwargs):
	try:
		key = get_hash_digest(raw_key, rounds=get_rounds(raw_key))

		def decrypt_process(f_path, output_file_path=None, to_mem=False, *args, **kwargs):
			ifile_path = get_intermediate_file_path(f_path)
			decode_chunk = kwargs.pop('decode_chunk', True)
			data = None
			_rounds = None
			is_first = kwargs.get('first')
			
			data = decrypt_to_file(
				cipher_algos[1],
				key[hash_bytes_half:],
				f_path,
				output_file_path=ifile_path,
				decode_chunk=decode_chunk,
				*args,
				**kwargs
			)

			kwargs.pop('first', None)

			if is_first:
				_rounds = data[0]
				data = data[1]

			if to_mem:
				data = decrypt_to_mem(
					cipher_algos[0], 
					key[:hash_bytes_half],
					ifile_path,
					*args,
					**kwargs
				)

			else:
				decrypt_to_file(
					cipher_algos[0],
					key[:hash_bytes_half],
					ifile_path,
					output_file_path=output_file_path,
					decode_chunk=decode_chunk,
					*args, 
					**kwargs
				)

			secure_delete(ifile_path)

			if is_first:
				return _rounds, data

			return data

		
		def _get_output_file_path():
			if to_mem:
				return None

			if output_file_path is None:
				return get_decrypt_file_path(file_path)
			
			return output_file_path
		
		def final_decrypt(file_path, output_file_path):
			output_file_path = _get_output_file_path()
			
			data = decrypt_process(
				file_path,
				output_file_path=output_file_path,
				to_mem=to_mem,
				decode_chunk=False,
				*args,
				**kwargs
			)

			secure_delete(file_path)

			return data

		_file_path = file_path
		prev_ifile_path = None

		ifile_path = get_intermediate_file_path(file_path)

		rounds, data = decrypt_process(
			_file_path,
			ifile_path,
			decode_chunk=False,
			first=True,
			*args,
			**kwargs
		)

		rounds_outside_loop = 2
		rounds -= rounds_outside_loop

		if rounds < 0:
			output_file_path = _get_output_file_path()

			if output_file_path is not None:
				shutil.move(ifile_path, output_file_path)
				return

			with open(ifile_path, 'r') as file:
				data = file.read()
				
			return data
		
		prev_ifile_path = ifile_path
		_file_path = ifile_path

		while rounds:		
			ifile_path = get_intermediate_file_path(file_path)

			decrypt_process(
				_file_path, 
				ifile_path,
				decode_chunk=False,
				*args, 
				**kwargs
			)
			
			secure_delete(prev_ifile_path)

			prev_ifile_path = ifile_path
			_file_path = ifile_path
			rounds -= 1


		data = final_decrypt(_file_path, output_file_path)		

		return data

	except Exception as err:
		remove_intermediate_files(os.path.dirname(file_path))
		raise err


def encrypt(raw_key, file_path, rounds=1, output_file_path=None, *args, **kwargs):
	try:
		key = get_hash_digest(raw_key, rounds=get_rounds(raw_key))
		
		def encrypt_process(f_path, output_file_path, *args, **kwargs):
			ifile_path = get_intermediate_file_path(f_path)

			rounds = kwargs.pop('rounds', None)

			encrypt_to_file(
				cipher_algos[0],
				key[:hash_bytes_half],
				f_path,
				output_file_path=ifile_path,
				*args,
				**kwargs
			)

			kwargs['rounds'] = rounds

			encrypt_to_file(
				cipher_algos[1], 
				key[hash_bytes_half:],
				ifile_path,
				output_file_path=output_file_path,
				*args, 
				**kwargs
			)

			secure_delete(ifile_path)


		base_rounds = rounds
		_file_path = file_path

		rounds_outside_loop = 1
		rounds -= rounds_outside_loop

		prev_ifile_path = None

		keep = not rounds

		while rounds:
			ifile_path = get_intermediate_file_path(file_path)

			encrypt_process(_file_path, ifile_path, *args, **kwargs)

			if prev_ifile_path is not None:
				secure_delete(prev_ifile_path)

			prev_ifile_path = ifile_path
			_file_path = ifile_path
			rounds -= 1

		if output_file_path is None:
			output_file_path = get_encrypt_file_path(file_path)

		encrypt_process(
			_file_path, 
			output_file_path,
			rounds=base_rounds,			
			*args,
			**kwargs
		)

		if not keep:
			secure_delete(_file_path)

	except Exception as err:
		remove_intermediate_files(os.path.dirname(file_path))
		raise err


def pad(chunk, block_size):
	return chunk + ((block_size - len(chunk) % block_size) * b' ')


def pad_if_needed(chunk, block_size):
	return pad(chunk, block_size) if len(chunk) % block_size != 0 else chunk


def _encrypt_to_file(
	input_file, encrypt, file_size, IV, output_file_path, block_size, **kwargs
):
	with open(output_file_path, 'wb') as output_file:
		rounds = kwargs.get('rounds')

		output_file_write = output_file.write

		output_file_write(file_size)
		output_file_write(IV)

		if rounds is not None:
			output_file_write(rounds)

		for chunk in file_read_generator(input_file, chunk_size):
			output_file_write(encrypt(
				pad_if_needed(chunk, block_size)
			))


def _encrypt_to_mem(input_file, encrypt, file_size, IV, block_size):
	ciphered_data = b''
	output_file_write = output_file.write

	ciphered_data += file_size
	ciphered_data += IV
	ciphered_data += kwargs.get('rounds', b'')

	for chunk in file_read_generator(input_file, chunk_size):
		ciphered_data += encrypt(
			pad_if_needed(chunk, block_size)
		)

	return ciphered_data.decode()


def _encrypt(algo_obj, key, file_path, encrypt_func, **kwargs):
	block_size = algo_obj.block_size
	output_file_path = kwargs.pop('output_file_path', False) or get_encrypt_file_path(file_path)
	file_size = get_file_size_zfill(file_path, block_size).encode()
	IV = get_random_bytes(block_size)

	if kwargs.get('rounds') is not None:
		kwargs['rounds'] = str(kwargs['rounds'])\
								.zfill(block_size)\
								.encode()	

	cipher = algo_obj.new(key, algo_obj.MODE_CBC, IV)

	with open(file_path, 'rb') as input_file:
		return encrypt_func(
			input_file,
			cipher.encrypt,
			file_size, 
			IV,
			output_file_path, 
			block_size,
			**kwargs
		)


def encrypt_to_file(algo_obj, key, file_path, **kwargs):
	return _encrypt(algo_obj, key, file_path, _encrypt_to_file, **kwargs)


def encrypt_to_mem(algo_obj, key, file_path, **kwargs):
	return _encrypt(algo_obj, key, file_path, _encrypt_to_mem, **kwargs)


def _decrypt_to_mem(file, decrypt, file_size, *args, **kwargs):
	deciphered_data = b''

	for chunk in file_read_generator(file, chunk_size):
		deciphered_data += decrypt(chunk)

	return deciphered_data[:file_size].decode()


def _decrypt_to_file(file, decrypt, file_size, file_path, *args, **kwargs):
	output_file_path = kwargs.pop('output_file_path', False) or get_decrypt_file_path(file_path)

	with open(output_file_path, 'wb') as output_file:
		output_file_write = output_file.write

		if kwargs.pop('decode_chunk', True):
			for chunk in file_read_generator(file, chunk_size):
				output_file_write(decrypt(chunk).decode())

		else:
			for chunk in file_read_generator(file, chunk_size):
				output_file_write(decrypt(chunk))

		output_file.truncate(file_size)


def _decrypt(algo_obj, key, file_path, decrypt_func, **kwargs):
	with open(file_path, 'rb') as file:
		block_size = algo_obj.block_size	
		file_size = int(file.read(block_size))
		IV = file.read(block_size)

		is_first = kwargs.get('first')

		if is_first:
			rounds = int(file.read(block_size))

		cipher = algo_obj.new(key, algo_obj.MODE_CBC, IV)
		decrypt = cipher.decrypt

		if is_first:
			return rounds, decrypt_func(file, decrypt, file_size, file_path, **kwargs)
			
		return decrypt_func(file, decrypt, file_size, file_path, **kwargs)


def decrypt_to_mem(algo_obj, key, file_path, **kwargs):
	return _decrypt(algo_obj, key, file_path, _decrypt_to_mem, **kwargs)


def decrypt_to_file(algo_obj, key, file_path, **kwargs):
	return _decrypt(algo_obj, key, file_path, _decrypt_to_file, **kwargs)