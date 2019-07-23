from .ulist import get_by_index
from .udict import OrderedDictExtended
from sys import argv


def get_argv(index):
	return get_by_index(index, argv)


opts_odict = OrderedDictExtended()

def get_params():
	if opts_odict:
		return opts_odict

	dash = '-'
	dbl_dash = '--'
	equal = '='
	skip = True
	new_index = 0

	def is_argv_last(value):
		return get_argv(-1) == value

	for index, option in enumerate(argv):
		if skip:
			skip = False
			continue

		if not option.startswith(dash):
			opts_odict[new_index] = option
			new_index += 1
			continue

		if option.startswith(dbl_dash) and option.find(equal) != -1:
			key, value = option.split(equal)
			opts_odict[key] = value
			continue

		next_value = get_argv(index + 1)

		if next_value:
			nv_startswith = next_value.startswith

			if nv_startswith(dash) or nv_startswith(dbl_dash) or next_value is None or is_argv_last(next_value):
				opts_odict[option] = 1
				continue

		else:
			opts_odict[option] = 1
			continue

		opts_odict[option] = next_value
		skip = True

	return opts_odict