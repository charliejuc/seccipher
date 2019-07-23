#!/usr/bin/python3

from lib.lcrypto import encrypt, decrypt
from utils.uparams import get_params
from utils.validation import valid_params
from termcolor import colored
from getpass import getpass
from sys import exit, stderr

def show_error(error):
	print(colored(error, 'red'), file=stderr)

def show_errors(errors):
	for message in errors:
		show_error(message)

def help():
	print(colored('Example: ./cipher.py (-c|-d) [-o] [options] file_path', 'green'))
	print('\t--rounds=[2]')


def run(params_odict):
	if not len(params_odict) or params_odict.get('-h'):
		help()
		exit(0)

	valid, errors = valid_params(params_odict)

	if not valid:
		show_errors(errors)
		exit(1)

	is_encrypt = params_odict.get('-c', False)
	is_decrypt = params_odict.get('-d', False)

	if is_encrypt and is_decrypt:
		show_error('"-c" and "-d" flags can not be used toguether.')
		exit(1)

	if not is_encrypt and not is_decrypt:
		show_error('You need use "-c" or "-d" flag.')
		exit(1)

	file_path = params_odict.last()
	output_file_path = params_odict.get('-o')

	key = getpass()
	rounds = int(params_odict.get('--rounds', 2))

	if is_encrypt:
		repeat_key = getpass('Repeat Password')

		if key != repeat_key:
			show_error('Passwords mismatch')
			exit(1)

		encrypt(key, file_path, output_file_path=output_file_path, rounds=rounds)

	elif is_decrypt:
		try:
			decrypt(key, file_path, output_file_path=output_file_path, rounds=rounds)

		except (UnicodeDecodeError, ValueError) as err:
			show_error('Incorrect password.')

			if params_odict.get('--debug') is not None:
				print(err)

			exit(1)


if __name__ == '__main__':
	run(get_params())