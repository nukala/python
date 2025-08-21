import argparse
from datetime import datetime
import os
from PIL import Image
import cv2
import numpy as np
from typing import Tuple, Optional


def parse_size(size_str: str) -> int:
    """Convert size string (e.g., '2k', '4m') to bytes."""
    size_str = size_str.lower()
    multiplier = 1
    if size_str.endswith('k'):
        multiplier = 1024
        size_str = size_str[:-1]
    elif size_str.endswith('m'):
        multiplier = 1024 * 1024
        size_str = size_str[:-1]
    return int(float(size_str) * multiplier)


def generate_output_filename(base_path: str, file_name: str) -> str:
    """Generate output filename with timestamp and handle conflicts."""
    now = datetime.now()
    month_name = now.strftime("%b").lower()
    file_part = "none"
    if os.path.extsep in file_name:
        file_part = file_name.split(os.path.extsep)[-2]
    print(f"  >>> file_name={file_name}, file_part={file_part}\n")

    base_filename = f"{file_part}-{now.strftime('%y')}{month_name}{now.strftime('%d')}"
    output_path = os.path.join(base_path, f"{base_filename}.jpg")
    
    if not os.path.exists(output_path):
        return output_path
    
    # Handle conflicts by appending minutes and seconds
    counter = 1
    while True:
        conflict_filename = f"{base_filename}{now.strftime('%M%S')}_{counter:02d}.jpg"
        output_path = os.path.join(base_path, conflict_filename)
        if not os.path.exists(output_path):
            return output_path
        counter += 1


def calculate_quality_metrics(original: np.ndarray, processed: np.ndarray) -> dict:
    """Calculate PSNR and SSIM between original and processed images."""
    mse = np.mean((original - processed) ** 2)
    if mse == 0:
        psnr = float('inf')
    else:
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    
    # Simple SSIM approximation (requires same dimensions)
    if original.shape == processed.shape:
        mu_x = np.mean(original)
        mu_y = np.mean(processed)
        sigma_x = np.std(original)
        sigma_y = np.std(processed)
        sigma_xy = np.mean((original - mu_x) * (processed - mu_y))
        ssim = ((2 * mu_x * mu_y + 1e-6) * (2 * sigma_xy + 1e-6)) / \
               ((mu_x**2 + mu_y**2 + 1e-6) * (sigma_x**2 + sigma_y**2 + 1e-6))
    else:
        ssim = None
    
    return {"psnr": psnr, "ssim": ssim}


def resize_and_compress_image(input_path: str, output_path: str, width: int, height: int, max_size: int) -> dict:
    """
    Resize JPEG image and compress if necessary to meet max file size.
    
    Args:
        input_path: Path to input JPEG image
        output_path: Path for output image
        width: Target width in pixels
        height: Target height in pixels
        max_size: Maximum file size in bytes
    
    Returns:
        Dictionary containing quality metrics (PSNR, SSIM)
    """
    # Read image with cv2
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError("Failed to read input image")
    
    original_img = img.copy()
    
    # Resize image
    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    
    # Convert to PIL for compression
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    # Initial save with high quality
    quality = 95
    pil_img.save(output_path, "JPEG", quality=quality)
    
    # Compress if file size exceeds max_size
    while os.path.getsize(output_path) > max_size and quality > 10:
        quality -= 5
        pil_img.save(output_path, "JPEG", quality=quality)
    
    # Read back processed image for quality metrics
    processed_img = cv2.imread(output_path)
    
    # Calculate quality metrics
    return calculate_quality_metrics(original_img, processed_img)


def main():
    """Main function to parse arguments and process image."""
    parser = argparse.ArgumentParser(description="Resize and compress JPEG images")
    parser.add_argument("--input", "-i", required=True, help="Input JPEG file path")
    parser.add_argument("--width", "-wd", type=int, required=True, help="Target width in pixels")
    parser.add_argument("--height", "-ht", type=int, required=True, help="Target height in pixels")
    parser.add_argument("--max-size", "-m", default="1m", help="Max file size (e.g., 2k, 4m)")
    
    args = parser.parse_args()
    
    output_path = generate_output_filename(os.path.dirname(args.input) or ".", os.path.basename(args.input))
    max_size = parse_size(args.max_size)
    
    metrics = resize_and_compress_image(args.input, output_path, args.width, args.height, max_size)
    
    print(f"Output saved to: {output_path}")
    print(f"Quality metrics: PSNR={metrics['psnr']:.2f}, SSIM={metrics['ssim']:.4f if metrics['ssim'] is not None else 'N/A'}")


if __name__ == "__main__":
    main()
