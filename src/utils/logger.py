from datetime import datetime


def log(input_string=""):
	"""
	write a function that accepts strings arguments and writes them to a file
	:param input_string: string to write to file
	:return:
	"""
	# get current timestamp and format as [YYYY-MM-DD HH:MM:SS]
	current_timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

	# open file in append mode
	print(f"{current_timestamp} {input_string}")