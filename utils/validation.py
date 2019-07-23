from os import path

def base_validation(value, message, validation_func=bool):
	if validation_func(value):
		return (True, None)

	message = message\
				.format(value=value)

	return (False, message)


def file_validation(file_path):
	message = '"{value}" is not a file.'

	return base_validation(file_path, message, path.isfile)


def flag_validation(value):
	message = '"{value}" is not a valid flag value.'

	return base_validation(value, message)


def int_validation(value):
	message = '"{value}" is not a valid int value.'

	def is_int(value):
		try:
			int(value)
			return True

		except ValueError:
			return False

	return base_validation(value, message, is_int)


def str_validation(value):
	message = '"{value}" is not a valid string value.'

	def is_str(value):
		return isinstance(value, str)

	return base_validation(value, message, is_str)


validation_types = {
	0: file_validation,
	'file': file_validation,
	'flag': flag_validation,
	'int': int_validation,
	'str': str_validation
}

params_and_type = {
	-1: 'file',
	'-o': 'str',
	'-c': 'flag',
	'-d': 'flag',
	'--debug': 'flag',
	'--rounds': 'int',
}

required_params = [
	-1,
]

required_error = '"{name}" param is required.'


param_translate = {
	-1: 'File Path',
}


def translate_param(key):
	return param_translate.get(key, key)


def get_validation_by_type(_type):
	return validation_types[_type]


def rev_index(index, _len):
	if index >= 0:
		return index - _len

	return _len + index


def valid_params(params):
	errors = list()
	errors_append = errors.append
	not_found_required_params = list(required_params)

	def rev_index_in(index, params_len):
		return isinstance(index, int) and rev_index(index, params_len) in not_found_required_params

	def remove_index_from_not_found(index):
		index = not_found_required_params.index(index)
		del not_found_required_params[index]

	try:
		awni_len = len(params.get_awni())
		r_index = None
		check_rev_index = True

		for index, param in params.items():
			if index in not_found_required_params:
				check_rev_index = False
				remove_index_from_not_found(index)

			if check_rev_index and rev_index_in(index, awni_len):
				check_rev_index = True
				r_index = rev_index(index, awni_len)
				remove_index_from_not_found(r_index)

			try:
				_type = params_and_type[index]

			except KeyError as ke:
				if r_index is None:
					raise ke

				_type = params_and_type[r_index]

			valid, message = get_validation_by_type(_type)(param)

			if not valid:
				errors_append(message)

		if not_found_required_params:
			required_error_format = required_error.format
			for key in not_found_required_params:
				errors_append(
					required_error_format(name=translate_param(key))
				)

	except KeyError as ke:
		errors_append('Invalid param "{param}" with key "{key}"'\
			.format(param=param, key=index))

	return ( not bool(errors), errors )