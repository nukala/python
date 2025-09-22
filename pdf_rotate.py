from pypdf import PdfReader, PdfWriter
import sys

def rotate_pdf_clockwise(input_pdf_path, output_pdf_path, rotation_angle=90):
    """
    Rotates all pages of a PDF file clockwise by a specified angle and saves the result.

    Args:
        input_pdf_path (str): The path to the input PDF file.
        output_pdf_path (str): The path to save the rotated PDF file.
        rotation_angle (int): The angle of rotation in degrees (must be a multiple of 90).
    """
    try:
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            page.rotate(rotation_angle)  # Rotate the page clockwise
            writer.add_page(page)

        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)
        print(f"PDF rotated and saved successfully to: {output_pdf_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
input_file = sys.argv[1]  # Replace with your input PDF file name
output_file = sys.argv[2]  # Desired output file name

rotate_pdf_clockwise(input_file, output_file, 90)