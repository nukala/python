#!/usr/bin/env python3
# Unit tests for JPEG Compressor Tool

import os
import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import numpy as np
from typing import Dict, Any

# Import our module
from jpeg_compressor import (
    compress_jpeg, 
    measure_quality_difference, 
    get_non_conflicting_output_path,
    process_image_for_compression
)

class TestJpegCompressor(unittest.TestCase):
    """Test suite for JPEG compressor functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test image
        self.create_test_image()
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def create_test_image(self):
        """Create a test JPEG image for compression tests"""
        # Create a temporary file for our test image
        self.test_image_path = os.path.join(self.test_dir, "test_image.jpg")
        
        # Create a simple gradient image
        width, height = 800, 600
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        # Fill with a gradient pattern
        for i in range(width):
            for j in range(height):
                r = int(i / width * 255)
                g = int(j / height * 255)
                b = int((i + j) / (width + height) * 255)
                pixels[i, j] = (r, g, b)
        
        # Save as high quality JPEG
        img.save(self.test_image_path, 'JPEG', quality=95)
    
    def test_compress_jpeg_basic(self):
        """Test basic compression functionality"""
        # Compress the test image
        output_dir = self.test_dir
        results = compress_jpeg(self.test_image_path, output_dir, quality=50, verbosity=0)
        
        # Check if output file exists
        self.assertTrue(os.path.exists(results['output_path']))
        
        # Check if file size is reduced
        self.assertLess(results['compressed_size'], results['original_size'])
        
        # Check if percentage saved is calculated correctly
        expected_percentage = ((results['original_size'] - results['compressed_size']) / 
                              results['original_size'] * 100)
        self.assertAlmostEqual(results['percentage_saved'], expected_percentage, places=4)
    
    def test_compression_quality_levels(self):
        """Test multiple compression quality levels"""
        # Test with different quality settings
        quality_levels = [10, 50, 90]
        sizes = []
        
        for quality in quality_levels:
            results = compress_jpeg(self.test_image_path, self.test_dir, 
                                  quality=quality, verbosity=0)
            sizes.append(results['compressed_size'])
        
        # Lower quality should result in smaller file size
        self.assertGreater(sizes[1], sizes[0], "Medium quality should be larger than low quality")
        self.assertGreater(sizes[2], sizes[1], "High quality should be larger than medium quality")
    
    def test_filename_conflict_resolution(self):
        """Test filename conflict resolution with timestamp"""
        # Compress image first time
        results1 = compress_jpeg(self.test_image_path, self.test_dir, verbosity=0)
        
        # Rename the output file to match the original test image name
        output_dir = Path(self.test_dir)
        conflict_name = output_dir / "test_image.jpg"
        
        # Ensure our test works correctly if the implementation changes
        if not conflict_name.exists():
            shutil.copy(results1['output_path'], conflict_name)
        
        # Compress again - should generate a different filename
        results2 = compress_jpeg(self.test_image_path, self.test_dir, verbosity=0)
        
        # Check that the two output paths are different
        self.assertNotEqual(results1['output_path'], results2['output_path'])
        
        # Check that the second filename contains a timestamp
        output_file = os.path.basename(results2['output_path'])
        self.assertRegex(output_file, r'test_image-\d{4}\.jpg')
    
    def test_image_quality_metrics(self):
        """Test image quality metrics calculation"""
        # Compress with different quality levels
        high_quality = compress_jpeg(self.test_image_path, self.test_dir, 
                                   quality=90, verbosity=0)
        low_quality = compress_jpeg(self.test_image_path, self.test_dir, 
                                  quality=10, verbosity=0)
        
        # Higher quality should have better SSIM score
        self.assertGreater(
            high_quality['quality_metrics']['ssim'],
            low_quality['quality_metrics']['ssim']
        )
        
        # Higher quality should have better PSNR
        self.assertGreater(
            high_quality['quality_metrics']['psnr'],
            low_quality['quality_metrics']['psnr']
        )
        
        # Higher quality should have lower MSE
        self.assertLess(
            high_quality['quality_metrics']['mse'],
            low_quality['quality_metrics']['mse']
        )
    
    def test_input_validation(self):
        """Test input validation"""
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            compress_jpeg("nonexistent_file.jpg", self.test_dir, verbosity=0)
        
        # Create a non-JPEG file
        non_jpeg_path = os.path.join(self.test_dir, "test.txt")
        with open(non_jpeg_path, 'w') as f:
            f.write("This is not a JPEG file")
        
        # Test with non-JPEG file
        with self.assertRaises(ValueError):
            compress_jpeg(non_jpeg_path, self.test_dir, verbosity=0)
            
    def test_get_non_conflicting_output_path(self):
        """Test the method that generates non-conflicting output paths"""
        # Create a path object for output directory
        output_dir = Path(self.test_dir)
        
        # Test with a non-existent output file
        input_path = Path(self.test_image_path)
        output_path = get_non_conflicting_output_path(input_path, output_dir)
        expected_path = output_dir / f"{input_path.stem}.jpg"
        self.assertEqual(output_path, expected_path)
        
        # Test with an existing output file (should add timestamp)
        # First create the conflict
        conflict_path = output_dir / f"{input_path.stem}.jpg"
        with open(conflict_path, 'w') as f:
            f.write("dummy content")
            
        # Now get a non-conflicting path
        output_path = get_non_conflicting_output_path(input_path, output_dir)
        self.assertNotEqual(output_path, conflict_path)
        self.assertRegex(output_path.name, r'test_image-\d{4}\.jpg')
    
    def test_process_image_for_compression(self):
        """Test the image processing method"""
        # Create a grayscale test image
        grayscale_path = os.path.join(self.test_dir, "grayscale.jpg")
        grayscale_img = Image.new('L', (100, 100), 128)  # L is for grayscale
        grayscale_img.save(grayscale_path)
        
        # Open the grayscale image and process it
        with Image.open(grayscale_path) as img:
            self.assertEqual(img.mode, 'L')
            processed = process_image_for_compression(img)
            self.assertEqual(processed.mode, 'RGB')
        
        # Test with an already RGB image
        with Image.open(self.test_image_path) as img:
            self.assertEqual(img.mode, 'RGB')
            processed = process_image_for_compression(img)
            self.assertEqual(processed.mode, 'RGB')

if __name__ == '__main__':
    unittest.main()