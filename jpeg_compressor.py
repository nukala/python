#!/usr/bin/env python3
# JPEG Compressor Tool
# This script compresses JPEG images with configurable quality settings,
# measures space savings, and image quality differences.

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Union, Optional, Any, Tuple
import numpy as np
from PIL import Image
import cv2
import traceback
from skimage.metrics import structural_similarity as ssim


def get_non_conflicting_output_path(input_path: Path, output_dir: Path) -> Path:
    """
    Generate a non-conflicting output path for the compressed image.
    If a file with the same name exists, add a timestamp to avoid conflicts.
    
    Args:
        input_path: Path to the input image
        output_dir: Directory to save the compressed image
        
    Returns:
        Path object for the non-conflicting output path
    """
    base_filename = input_path.stem
    output_filename = f"{base_filename}.jpg"
    output_path = output_dir / output_filename
    
    # If output file exists, add timestamp to filename
    if output_path.exists():
        timestamp = datetime.now().strftime("%H%M")
        output_filename = f"{base_filename}-{timestamp}.jpg"
        output_path = output_dir / output_filename
    
    return output_path


def process_image_for_compression(img: Image.Image) -> Image.Image:
    """
    Process the image before compression (e.g., convert to RGB if needed).
    
    Args:
        img: PIL Image object
        
    Returns:
        Processed PIL Image object ready for compression
    """
    # Make sure we're working with RGB (convert if needed)
    if img.mode != 'RGB':
        return img.convert('RGB')
    return img


def compress_jpeg(
    input_path: Union[str, Path], 
    output_dir: Union[str, Path] = "~/tmp", 
    quality: int = 80, 
    resize_factor: int = None,
    verbosity: int = 1
) -> Dict[str, Any]:
    """
    Compress a JPEG image to the specified quality and save to output directory.
    
    Args:
        input_path: Path to the input JPEG image
        output_dir: Directory to save compressed image (defaults to ~/tmp)
        quality: JPEG compression quality (0-100, lower means higher compression)
        resize_factor: To resize the image (0-100, lower means low resolution)
        verbosity: Level of verbosity (0=quiet, 1=normal, 2=detailed, 3=debug)
        
    Returns:
        Dictionary containing compression results and metrics
    """
    # Normalize input path
    input_path = Path(input_path).expanduser().resolve()
    
    # Make sure input file exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Verify input is a JPEG image
    if input_path.suffix.lower() not in ['.jpg', '.jpeg']:
        raise ValueError(f"Input file is not a JPEG image: {input_path}")
    
    # Normalize and create output directory if it doesn't exist
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get non-conflicting output path
    output_path = get_non_conflicting_output_path(input_path, output_dir)
    
    # Debug output in highest verbosity
    if verbosity >= 3:
        print(f"DEBUG: Input path normalized to: {input_path}")
        print(f"DEBUG: Output directory normalized to: {output_dir}")
        print(f"DEBUG: Output path set to: {output_path}")
    
    # Get original file size
    original_size = input_path.stat().st_size
    if verbosity >= 3:
        print(f"DEBUG: Original file size: {original_size} bytes")
    
    # Open and compress the image
    try:
        # Open with PIL for compression
        with Image.open(input_path) as img:
            if verbosity >= 3:
                print(f"DEBUG: Image opened successfully. Mode: {img.mode}, Size: {img.size}")
            
            if resize_factor and 1 < resize_factor < 100:
                new_width = int((resize_factor/100) * img.width)
                new_height = int((resize_factor/100) * img.height)
                msg_str = f"[{img.width}x{img.height}] ==>> [{new_width}x{new_height}]"
                img = img.resize((new_width, new_height), Image.LANCZOS)
                if verbosity >= 2:
                    print(f"Image resolution changed from [{msg_str}]")


            # Process the image (e.g., convert to RGB if needed)
            processed_img = process_image_for_compression(img)
            
            # Save compressed image
            processed_img.save(output_path, 'JPEG', quality=quality, optimize=True)
            if verbosity >= 3:
                print(f"DEBUG: Image saved successfully to {output_path}")
    except Exception as e:
        raise RuntimeError(f"Error compressing image: {e}")
    
    # Get compressed file size
    compressed_size = output_path.stat().st_size
    
    # Calculate size reduction
    size_reduction = original_size - compressed_size
    percentage_saved = (size_reduction / original_size) * 100
    
    if verbosity >= 3:
        print(f"DEBUG: Compressed file size: {compressed_size} bytes")
        print(f"DEBUG: Size reduction: {size_reduction} bytes ({percentage_saved:.2f}%)")
    
    # Measure image quality difference
    quality_metrics = measure_quality_difference(str(input_path), str(output_path), resize_factor=resize_factor)
    
    if verbosity >= 3:
        print(f"DEBUG: Quality metrics calculated: {quality_metrics}")
    
    # Prepare the results
    results = {
        'input_path': str(input_path),
        'output_path': str(output_path),
        'original_size': original_size,
        'compressed_size': compressed_size,
        'bytes_saved': size_reduction,
        'percentage_saved': percentage_saved,
        'quality_setting': quality,
        'quality_metrics': quality_metrics
    }
    
    # Print results based on verbosity level
    if verbosity >= 1:
        print(f"\nJPEG Compression Results:")
        print(f"  Original file: {input_path}")
        print(f"  Compressed file: {output_path}")
        print(f"  Original size: {format_size(original_size)}")
        print(f"  Compressed size: {format_size(compressed_size)}")
        print(f"  Space saved: {format_size(size_reduction)} ({percentage_saved:.2f}%)")
    
    if verbosity >= 2:
        print("\nImage Quality Metrics:")
        print(f"  PSNR: {quality_metrics['psnr']:.2f} dB (higher = better quality)")
        if not resize_factor:
            print(f"  SSIM index: {quality_metrics['ssim']:.4f} (1.0 = identical)")
            print(f"  MSE: {quality_metrics['mse']:.2f} (lower = better quality)")
    
    return results


def measure_quality_difference(original_path: str, compressed_path: str, resize_factor: int = None) -> Dict[str, float]:
    """
    Measure quality differences between original and compressed images.
    
    Args:
        original_path: Path to the original image
        compressed_path: Path to the compressed image
        
    Returns:
        Dictionary containing quality metrics (SSIM, PSNR, MSE)
    """
    # Read images using OpenCV
    original = cv2.imread(original_path)
    compressed = cv2.imread(compressed_path)
    
    # Convert to grayscale for SSIM calculation
    original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    compressed_gray = cv2.cvtColor(compressed, cv2.COLOR_BGR2GRAY)
    
    # Calculate SSIM (Structural Similarity Index)
    ssim_index = 0.0
    mse = 100
    if not resize_factor: 
        ssim_index = ssim(original_gray, compressed_gray)
        # Calculate PSNR (Peak Signal-to-Noise Ratio)
        mse = np.mean((original - compressed) ** 2)

    if mse == 0:  # Images are identical
        psnr = float('inf')
    else:
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    
    return {
        'ssim': ssim_index,  # 1.0 means identical images
        'psnr': psnr,        # Higher is better (typically 30-50 dB is good)
        'mse': mse           # Lower is better (Mean Square Error)
    }


def format_size(size_bytes: int) -> str:
    """Format file size in a human-readable way"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} KB"
    else:
        return f"{size_bytes/(1024*1024):.2f} MB"


def main() -> int:
    """Main entry point for CLI usage"""
    parser = argparse.ArgumentParser(description='Compress JPEG images and measure quality differences')
    parser.add_argument('input', help='Path to input JPEG file')
    parser.add_argument('--output-dir', '-o', default='~/tmp', 
                        help='Output directory (default: ~/tmp)')
    parser.add_argument('--quality', '-q', type=int, default=80, 
                        help='JPEG quality (0-100, default: 80)')
    parser.add_argument('--resize', '-r', type=int, default=None, 
                        help='To resize image resolution (0-100, default: 75)')
    
    # Add verbosity options with multiple levels
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('--quiet', action='store_true', 
                              help='Suppress all output')
    verbosity_group.add_argument('-v', '--verbose', action='count', default=1,
                              help='Increase verbosity (can be used multiple times, e.g. -vvv)')
    verbosity_group.add_argument('--verbosity', type=int, choices=[0, 1, 2, 3], default=1,
                              help='Set verbosity level (0=quiet, 1=normal, 2=detailed, 3=debug)')
    
    args = parser.parse_args()
    
    # Determine verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose is not None:
        verbosity = min(args.verbose, 3)  # Cap at level 3
    else:
        verbosity = args.verbosity
    
    try:
        compress_jpeg(args.input, args.output_dir, args.quality, resize_factor = args.resize, verbosity=verbosity)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if verbosity > 0:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
