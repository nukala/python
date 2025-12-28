import argparse
from datetime import datetime
from pathlib import Path
from PIL import Image
from pillow_heif import register_heif_opener
from ghsv import dbgln


class HeicJpeg:
	def __init__(self):
		parser = argparse.ArgumentParser(description="To convert HEIC (iPhone) to JPEG format. "
													 "Does not overwrite existing files")
		parser.add_argument("-i", "--input", required=True, help="Input HEIF file path")
		parser.add_argument("-j", "--jpeg", help="name of the jpeg file, extension jpeg will be added if required.")
		parser.add_argument("-p", "--parent-path", default="C:/filre/media/pictures",
							help="Parent path for all images [filre/media/pictures]")
		parser.add_argument("--child-path", "-c", help="optional child path under the parent",
							default=None)
		parser.add_argument("-yr", "--yr_sep", help="Use 4 digit-year as a seperator [False]",
							default=False, action="store_true")
		parser.add_argument("-v", action="count", dest="verbosity", default=0,
							help='Increase verbosity (can be used multiple times, e.g. -vvv)')
		parser.add_argument('--verbose', type=int, default=0, dest="verbosity",
                        help="Enable verbosity by specifying a number")

		self.args = parser.parse_args()
		register_heif_opener()

	def convert_heic_to_jpg(self, heic_filepath: str, jpg_filepath: str, overwrite: bool = False):
		if not overwrite:
			import os
			if os.path.exists(jpg_filepath):
				dbgln(f"{jpg_filepath} already exists, not overwriting", 0, self.args.verbosity)
				return

		try:
			img = Image.open(heic_filepath)
			img = img.convert('RGB')
			img.save(jpg_filepath, 'jpeg')
			dbgln(f"Converted {heic_filepath} to {jpg_filepath}", 2, self.args.verbosity)
		except Exception as e:
			print(f"Error converting {heic_filepath}: {e}")

	@staticmethod
	def get_current_year() -> str:
		"""
		returns current year as a string
		"""
		return f"{datetime.now().year}"

	def get_output_dir(self, mkdir: bool = True, child_path: str = None, yrsep: bool = False) -> str:
		output_dir = f"{self.args.parent_path}"
		if yrsep:
			output_dir = f"{output_dir}/{self.get_current_year()}"
		if child_path:
			output_dir = f"{output_dir}/{child_path}"

		if mkdir:
			output_path = Path(output_dir)
			if not output_path.exists():
				dbgln(f"\"{output_dir}\" does not exist. making!", 1, self.args.verbosity)
				# md parents as needed, don't barf if exists
				output_path.mkdir(parents=True, exist_ok=True)
		dbgln(f"output_dir=[{output_dir}]", 2, self.args.verbosity)
		return output_dir

	def get_jpeg_filepath(self, dirname: str = None) -> str:
		fname = self.args.jpeg
		if fname is None:
			dbgln(f"fname={fname} is None, using heic", 3, self.args.verbosity)
			fname = self.args.input.split('.')[0]
			dbgln(f"input={self.args.input}, fname={fname}", 4, self.args.verbosity)
		if ".jpg" in fname or ".jpeg" in fname:
			pass
		else:
			dbgln(f"appending .jpeg", 3, self.args.verbosity)
			fname += ".jpeg"

		if dirname:
			fname = dirname + "/" + fname
		dbgln(f"fname=[{fname}]", 2, self.args.verbosity)
		return fname


if __name__ == "__main__":
	converter = HeicJpeg()
	heic_path = converter.args.input
	output_dir = converter.get_output_dir(True, converter.args.child_path)
	jpg_filepath = converter.get_jpeg_filepath(output_dir)

	converter.convert_heic_to_jpg(heic_path, jpg_filepath)
	print(f"fxt {jpg_filepath}")