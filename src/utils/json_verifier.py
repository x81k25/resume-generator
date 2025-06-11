def is_array_of_strings(data):
	# First check if it's a list
	if not isinstance(data, list):
		return False

	# If the list is empty, we'll return False
	if not data:
		return False

	# Check if all items are strings
	return all(isinstance(item, str) for item in data)


def is_array_of_objects(data):
	# First check if it's a list
	if not isinstance(data, list):
		return False

	# If the list is empty, we'll return False
	if not data:
		return False

	# Check if all items are dictionaries
	return all(isinstance(item, dict) for item in data)


def is_object(data):
	# First check if it's a dictionary
	if not isinstance(data, dict):
		return False

	# Check if the dictionary is empty
	if not data:
		return False

	# Check if all keys are strings and all values are also strings
	return all(isinstance(key, str) and isinstance(value, str) for key, value in
			   data.items())