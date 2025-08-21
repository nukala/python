import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
from typing import Optional
from heic_jpg import HeicJpeg


class TestGetOutputDir:
	"""Test cases for the get_output_dir method."""

	@pytest.fixture
	def mock_instance(self) -> Mock:
		"""Create a mock instance with required attributes."""
		instance = Mock()
		instance.args = Mock()
		instance.args.parent_path = "/test/parent"
		instance.dbgln = Mock()  # Mock the dbgln method
		return instance

	# @WorthLooking  since file imports, datetime patch it this way
	@patch('heic_jpg.datetime')
	def test_get_output_dir_basic(self, mock_datetime: Mock, mock_instance: Mock) -> None:
		"""Test basic functionality with current year."""
		# Arrange
		mock_now = Mock()
		mock_now.strftime.return_value = "2024"
		mock_datetime.now.return_value = mock_now

		# Import and bind the method
		result = HeicJpeg.get_output_dir(mock_instance, mkdir=False)

		# Assert
		assert result == "/test/parent/2024"
		mock_datetime.now.assert_called_once()
		mock_now.strftime.assert_called_once_with("%Y")

	@patch('heic_jpg.datetime')
	def test_get_output_dir_with_child_path(self, mock_datetime: Mock, mock_instance: Mock) -> None:
		"""Test with child_path parameter."""
		# Arrange
		mock_now = Mock()
		mock_now.strftime.return_value = "2024"
		mock_datetime.now.return_value = mock_now

		# Import and bind the method
		result = HeicJpeg.get_output_dir(mock_instance, mkdir=False, child_path="subfolder")

		# Assert
		assert result == "/test/parent/2024/subfolder"

	@patch('heic_jpg.datetime')
	@patch('heic_jpg.Path')
	def test_get_output_dir_mkdir_true_path_exists(
			self, mock_path_class: Mock, mock_datetime: Mock, mock_instance: Mock
	) -> None:
		"""Test mkdir=True when path already exists."""
		# Arrange
		mock_now = Mock()
		mock_now.strftime.return_value = "2024"
		mock_datetime.now.return_value = mock_now

		mock_path_instance = Mock()
		mock_path_instance.exists.return_value = True
		mock_path_class.return_value = mock_path_instance

		# Import and bind the method
		result = HeicJpeg.get_output_dir(mock_instance, mkdir=True)

		# Assert
		assert result == "/test/parent/2024"
		mock_path_class.assert_called_once_with("/test/parent/2024")
		mock_path_instance.exists.assert_called_once()
		mock_path_instance.mkdir.assert_not_called()

	@patch('heic_jpg.datetime')
	@patch('heic_jpg.Path')
	def test_get_output_dir_mkdir_true_path_not_exists(
			self, mock_path_class: Mock, mock_datetime: Mock, mock_instance: Mock
	) -> None:
		"""Test mkdir=True when path does not exist."""
		# Arrange
		mock_now = Mock()
		mock_now.strftime.return_value = "2024"
		mock_datetime.now.return_value = mock_now

		mock_path_instance = Mock()
		mock_path_instance.exists.return_value = False
		mock_path_class.return_value = mock_path_instance

		# Import and bind the method
		result = HeicJpeg.get_output_dir(mock_instance, mkdir=True)

		# Assert
		assert result == "/test/parent/2024"
		mock_path_class.assert_called_once_with("/test/parent/2024")
		mock_path_instance.exists.assert_called_once()
		mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

	@patch('heic_jpg.datetime')
	def test_get_output_dir_different_years(self, mock_datetime: Mock, mock_instance: Mock) -> None:
		"""Test with different years."""
		# Arrange
		mock_now = Mock()
		mock_now.strftime.return_value = "2023"
		mock_datetime.now.return_value = mock_now

		# Import and bind the method
		result = HeicJpeg.get_output_dir(mock_instance, mkdir=False)

		# Assert
		assert result == "/test/parent/2023"

	@patch('heic_jpg.datetime')
	@patch('heic_jpg.Path')
	def test_get_output_dir_with_child_path_and_mkdir(
			self, mock_path_class: Mock, mock_datetime: Mock, mock_instance: Mock
	) -> None:
		"""Test with both child_path and mkdir=True."""
		# Arrange
		mock_now = Mock()
		mock_now.strftime.return_value = "2024"
		mock_datetime.now.return_value = mock_now

		mock_path_instance = Mock()
		mock_path_instance.exists.return_value = False
		mock_path_class.return_value = mock_path_instance

		# Import and bind the method
		result = HeicJpeg.get_output_dir(mock_instance, mkdir=True, child_path="data/output")

		# Assert
		assert result == "/test/parent/2024/data/output"
		mock_path_class.assert_called_once_with("/test/parent/2024/data/output")
		mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

	@patch('heic_jpg.datetime')
	def test_get_output_dir_empty_child_path(self, mock_datetime: Mock, mock_instance: Mock) -> None:
		"""Test with empty string child_path."""
		# Arrange
		mock_now = Mock()
		mock_now.strftime.return_value = "2024"
		mock_datetime.now.return_value = mock_now

		# Import and bind the method
		result = HeicJpeg.get_output_dir(mock_instance, mkdir=False, child_path="")

		# Assert
		assert result == "/test/parent/2024"

	@patch('heic_jpg.datetime')
	def test_get_output_dir_none_child_path(self, mock_datetime: Mock, mock_instance: Mock) -> None:
		"""Test with None child_path (default)."""
		# Arrange
		mock_now = Mock()
		mock_now.strftime.return_value = "2024"
		mock_datetime.now.return_value = mock_now

		# Import and bind the method
		result = HeicJpeg.get_output_dir(mock_instance, mkdir=False, child_path=None)

		# Assert
		assert result == "/test/parent/2024"

	def test_get_output_dir_dbgln_calls_ignored(self, mock_instance: Mock) -> None:
		"""Test that dbgln calls are properly mocked and don't affect functionality."""
		with patch('heic_jpg.datetime') as mock_datetime:
			mock_now = Mock()
			mock_now.strftime.return_value = "2024"
			mock_datetime.now.return_value = mock_now

			# Import and bind the method
			result = HeicJpeg.get_output_dir(mock_instance, mkdir=False)

			# Assert
			assert result == "/test/parent/2024"
			# Verify dbgln was called (but we don't care about the specifics)
			assert mock_instance.dbgln.called
