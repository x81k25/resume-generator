import pytest
from datetime import datetime
from unittest.mock import patch
from io import StringIO
import re
from src.utils.logger import log  # Replace 'your_module' with actual module name


def test_log_format():
	"""Test that the log output follows the expected format"""
	# Capture stdout
	with patch('sys.stdout', new=StringIO()) as fake_output:
		test_message = "Test message"
		log(test_message)
		output = fake_output.getvalue().strip()

		# Define expected timestamp format pattern
		timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'

		# Check if output matches expected pattern
		assert re.match(f'{timestamp_pattern} {test_message}', output), \
			f"Output '{output}' doesn't match expected format"


def test_log_special_characters():
	"""Test logging special characters"""
	special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
	with patch('sys.stdout', new=StringIO()) as fake_output:
		log(special_chars)
		output = fake_output.getvalue().strip()

		# Verify special characters are preserved
		assert output.endswith(special_chars), \
			"Special characters were not preserved in output"


def test_log_multiline_string():
	"""Test logging a multiline string"""
	multiline = "Line 1\nLine 2\nLine 3"
	with patch('sys.stdout', new=StringIO()) as fake_output:
		log(multiline)
		output = fake_output.getvalue().strip()

		# Verify multiline string is preserved
		assert output.endswith(multiline), \
			"Multiline string was not preserved in output"


def test_log_non_string_input():
	"""Test logging non-string inputs"""
	test_cases = [
		(123, "123"),
		(3.14, "3.14"),
		(["a", "b"], "['a', 'b']"),
		({"key": "value"}, "{'key': 'value'}")
	]

	for input_val, expected_str in test_cases:
		with patch('sys.stdout', new=StringIO()) as fake_output:
			log(input_val)
			output = fake_output.getvalue().strip()

			# Verify non-string input is converted to string representation
			assert output.endswith(expected_str), \
				f"Non-string input {input_val} was not properly converted"


if __name__ == '__main__':
	pytest.main([__file__])