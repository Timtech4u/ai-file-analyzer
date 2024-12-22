import pytest
from pathlib import Path
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import validate_file, Config, generate_smart_summary, process_image
from unittest.mock import Mock, patch
import io

class MockUploadedFile:
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size

def test_validate_file_size():
    """Test file size validation."""
    # Test file within size limit
    small_file = MockUploadedFile("test.pdf", Config.MAX_FILE_SIZE - 1000)
    is_valid, error = validate_file(small_file)
    assert is_valid
    assert error == ""

    # Test file exceeding size limit
    large_file = MockUploadedFile("test.pdf", Config.MAX_FILE_SIZE + 1000)
    is_valid, error = validate_file(large_file)
    assert not is_valid
    assert "File size exceeds" in error

def test_validate_file_type():
    """Test file type validation."""
    # Test valid file type
    valid_file = MockUploadedFile("test.pdf", 1000)
    is_valid, error = validate_file(valid_file)
    assert is_valid
    assert error == ""

    # Test invalid file type
    invalid_file = MockUploadedFile("test.invalid", 1000)
    is_valid, error = validate_file(invalid_file)
    assert not is_valid
    assert "Unsupported file type" in error

@pytest.mark.asyncio
async def test_generate_smart_summary():
    """Test summary generation."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test summary"))]
    mock_client.chat.completions.create.return_value = mock_response

    summary = generate_smart_summary("Test content", mock_client)
    assert summary == "Test summary"
    mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_process_image():
    """Test image processing."""
    # Create a temporary test image
    test_image = Path("test_image.jpg")
    test_image.write_bytes(b"fake image data")

    try:
        mock_client = Mock()
        mock_result = Mock()
        mock_result.text_content = "Test image description"
        mock_markitdown = Mock()
        mock_markitdown.convert.return_value = mock_result

        with patch("app.MarkItDown", return_value=mock_markitdown):
            description, image_data = process_image(str(test_image), mock_client)

        assert description == "Test image description"
        assert image_data == b"fake image data"
        mock_markitdown.convert.assert_called_once()

    finally:
        # Clean up
        test_image.unlink()

def test_config_loading():
    """Test configuration loading."""
    assert hasattr(Config, 'OPENAI_API_KEY')
    assert hasattr(Config, 'DEBUG')
    assert hasattr(Config, 'MAX_FILE_SIZE')
    assert hasattr(Config, 'MODEL_NAME')

    assert isinstance(Config.MAX_FILE_SIZE, int)
    assert Config.MODEL_NAME == "gpt-4" 