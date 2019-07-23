from os import path
from uuid import uuid4

output_ext = '.pwu'
output_ext_len = len(output_ext)

output_path = '{file_path}' + output_ext
output_path_format = output_path.format

intermediate_file_ext = '.hpwu'
intermediate_file_path = '{file_path}' + intermediate_file_ext
intermediate_file_path_format = intermediate_file_path.format


def get_encrypt_file_path(file_path):
	return output_path_format(file_path=file_path)


def get_decrypt_file_path(encrypt_file_path):
	return encrypt_file_path[:-output_ext_len]


def get_intermediate_file_path(file_path):
	file_path = path.join(
		path.dirname(file_path),
		uuid4().hex
	)
	
	return intermediate_file_path_format(file_path=file_path)