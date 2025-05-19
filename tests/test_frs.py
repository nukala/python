import pytest
from basern.frs import FrsApp

#### AI ###
# Given ```static method body``` write add pytest unit-tests
# assume that this is the first set of pytest tests for this code. 
# Assume that this method is embedded inside a class called SomeApp. 
# Use type safe code
# Please assume unknown_args will be array parameter.
#
# asked about pytest fixture -> went down a rabbit hole and decided to use a static wrapper method 
#  to improve readability
###


def parse(val: str, verbose: bool = False) -> int:
	"""Method to be tested. Makes tests an easy-read"""
	ua = ["", f"{val}"]
	return FrsApp.parse_income_from_args(ua, verbose)


class TestParseIncOperations:

	def test_parse_inc_with_integer(self) -> None:
		"""Test parse_inc with a regular integer."""
		result = parse("5000")
		assert result == 5000
		assert isinstance(result, int)

	def test_parse_inc_with_float(self) -> None:
		"""Test parse_inc with a float value."""
		result = parse("5000.5")
		assert result == 5000
		assert isinstance(result, int)

	def test_parse_inc_with_k_lowercase(self) -> None:
		"""Test parse_inc with lowercase 'k' suffix."""
		result = parse("5k")
		assert result == 5000
		assert isinstance(result, int)

	def test_parse_inc_with_k_uppercase(self) -> None:
		"""Test parse_inc with uppercase 'K' suffix."""
		result = parse("5K")
		assert result == 5000
		assert isinstance(result, int)

	def test_parse_inc_with_small_value(self) -> None:
		"""Test parse_inc with value less than 1000."""
		result = parse("5")
		assert result == 5000
		assert isinstance(result, int)

	def test_parse_inc_with_small_float_value(self) -> None:
		"""Test parse_inc with float value less than 1000."""
		result = parse("5.5")
		assert result == 5500
		assert isinstance(result, int)

	def test_parse_inc_with_small_k_value(self) -> None:
		"""Test parse_inc with 'k' suffix on small value."""
		result = parse("0.5k", True)
		assert result == 500
		assert isinstance(result, int)

	def test_parse_inc_value_error(self) -> None:
		"""Test parse_inc with non-numeric value."""
		with pytest.raises(ValueError):
			parse("not_a_number")
