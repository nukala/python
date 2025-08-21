import pytest
import os
import cv2
import numpy as np
from datetime import datetime
from PIL import Image
from resize_image import parse_size, generate_output_filename, calculate_quality_metrics, resize_and_compress_image

@pytest.fixture
def temp_image(tmp_path):
    """Create a temporary JPEG image for testing."""
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    img_path = tmp_path / "test.jpg"
    cv2.imwrite(str(img_path), img)
    return str(img_path)

def test_parse_size():
    """Test size string parsing."""
    assert parse_size("2k") == 2048
    assert parse_size("4M") == 4 * 1024 * 1024
    assert parse_size("1000") == 1000
    assert parse_size("1.5m") == 1.5 * 1024 * 1024
    with pytest.raises(ValueError):
        parse_size("invalid")

def test_generate_output_filename(tmp_path):
    """Test output filename generation and conflict resolution."""
    base_path = str(tmp_path)
    filename = generate_output_filename(base_path, "foo.jpg")
    
    now = datetime.now()
    expected_prefix = f"{now.strftime('%y')}{now.strftime('%b').lower()}{now.strftime('%d')}"
    assert filename.startswith(os.path.join(base_path, expected_prefix))
    assert filename.endswith(".jpg")
    
    # Test conflict resolution
    with open(filename, "w") as f:
        f.write("test")
    new_filename = generate_output_filename(base_path)
    assert new_filename != filename
    assert f"_{now.strftime('%M%S')}_" in new_filename

def test_calculate_quality_metrics():
    """Test quality metrics calculation."""
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    same_img = img.copy()
    diff_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
    
    metrics_same = calculate_quality_metrics(img, same_img)
    assert metrics_same["psnr"] == float('inf')
    assert metrics_same["ssim"] == pytest.approx(1.0, abs=1e-4)
    
    metrics_diff = calculate_quality_metrics(img, diff_img)
    assert metrics_diff["psnr"] < 20
    assert metrics_diff["ssim"] < 0.5
    
    # Test different dimensions
    small_img = np.ones((50, 50, 3), dtype=np.uint8) * 255
    metrics_small = calculate_quality_metrics(img, small_img)
    assert metrics_small["ssim"] is None

def test_resize_and_compress_image(temp_image, tmp_path):
    """Test image resizing and compression."""
    output_path = str(tmp_path / "output.jpg")
    metrics = resize_and_compress_image(temp_image, output_path, 50, 50, 1000)
    
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) <= 1000
    img = cv2.imread(output_path)
    assert img.shape[:2] == (50, 50)
    assert metrics["psnr"] > 0
    assert metrics["ssim"] is not None

def test_resize_and_compress_image_invalid_input(tmp_path):
    """Test handling of invalid input file."""
    with pytest.raises(ValueError):
        resize_and_compress_image("nonexistent.jpg", str(tmp_path / "output.jpg"), 50, 50, 1000)
