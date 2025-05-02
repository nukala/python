# JPEG Compressor Tool

A Python utility for compressing JPEG images with quality metrics and space savings analysis.

## Features

- Compress JPEG images with configurable quality settings
- Measure and report space savings (bytes and percentage)
- Evaluate image quality loss using multiple metrics:
  - SSIM (Structural Similarity Index)
  - PSNR (Peak Signal-to-Noise Ratio)
  - MSE (Mean Square Error)
- Cross-platform support (macOS, Windows, Linux)
- Automatic file naming with timestamp on conflicts
- Multiple verbosity levels for detailed output
- Type-hinted code for better maintainability
- Modular design with separate methods for path resolution and image processing
- Comprehensive unit tests

## Installation

1. Clone this repository or download the files
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
python jpeg_compressor.py input.jpg [options]
```

Options:
- `--output-dir` or `-o`: Output directory (default: ~/tmp)
- `--quality` or `-q`: JPEG quality (0-100, default: 80)
- `--quiet`: Suppress all output
- `-v` or `--verbose`: Increase verbosity (can be used multiple times, e.g. -vvv)
- `--verbosity LEVEL`: Set verbosity level (0=quiet, 1=normal, 2=detailed, 3=debug)

### Verbosity Levels

- **Level 0 (--quiet)**: No output
- **Level 1 (default)**: Basic compression results and space savings
- **Level 2 (-v -v)**: Level 1 + detailed quality metrics 
- **Level 3 (-v -v -v)**: Level 2 + debug information

### As a Module

```python
from jpeg_compressor import compress_jpeg

results = compress_jpeg(
    input_path='path/to/image.jpg',
    output_dir='~/tmp',
    quality=80,
    verbosity=1  # Set verbosity level (0-3)
)

# Access results
print(f"Space saved: {results['bytes_saved']} bytes")
print(f"Quality SSIM: {results['quality_metrics']['ssim']}")
```

## Understanding Quality Metrics

1. **SSIM (Structural Similarity Index)**
   - Range: 0.0 to 1.0
   - 1.0 means identical images
   - Values above 0.95 typically indicate good quality

2. **PSNR (Peak Signal-to-Noise Ratio)**
   - Measured in dB (decibels)
   - Higher values indicate better quality
   - Typical values for acceptable quality: 30-50 dB

3. **MSE (Mean Square Error)**
   - Lower values indicate better quality
   - 0 means identical images

## Running Tests

```bash
python -m unittest test_jpeg_compressor.py
```

## Notes

- The tool will automatically create the output directory if it doesn't exist
- If an output file with the same name already exists, a timestamp will be added to avoid overwriting
- For extremely large images, you may need more RAM

## Requirements

- Python 3.6+
- Dependencies listed in requirements.txt:
  - Pillow: Image processing
  - OpenCV: Image comparison and metrics
  - scikit-image: SSIM calculation
  - numpy: Numerical operations