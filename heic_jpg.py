import argparse
from datetime import datetime
from pathlib import Path
from PIL import Image
from pillow_heif import register_heif_opener


class HeicJpeg:
	# jun09> newer version in ghsv
	def dbgln(self, msg: str, level: int = 0):
		if level < 0:
			return

		if level <= self.args.verbosity:
			dbg_pfx = ' ' * level
			# there is a one-line style RNTODO
			nl = "\n"
			if nl in msg:
				nl = ""

			print(f"{dbg_pfx}{msg}{nl}")
		return

	def __init__(self):
		parser = argparse.ArgumentParser(description="To convert HEIC (iPhone) to JPEG format.")
		parser.add_argument("--input", "-i", required=True, help="Input HEIF file path")
		parser.add_argument("--jpeg", "-j", help="name of the jpeg file, extension jpeg will be added if required.")
		parser.add_argument("--parent-path", "--parent", "-p", default="C:/filre/media/pictures",
							help="Parent path for all images. 4-digit-year subfolder WILL be used")
		parser.add_argument("--child-path", "--child", "-c", help="optional child path under the parent")
		# example of using vvv with dbg and different destination
		parser.add_argument("-v", action="count", dest="verbosity", default=0,
							help='Increase verbosity (can be used multiple times, e.g. -vvv)')

		self.args = parser.parse_args()
		register_heif_opener()

	def convert_heic_to_jpg(self, heic_filepath: str, jpg_filepath: str):
		try:
			img = Image.open(heic_filepath)
			img = img.convert('RGB')
			img.save(jpg_filepath, 'jpeg')
			self.dbgln(f"Converted {heic_filepath} to {jpg_filepath}", 2)
			print(f"fxt {jpg_filepath}")
		except Exception as e:
			print(f"Error converting {heic_filepath}: {e}")

	def get_output_dir(self, mkdir: bool = True, child_path: str = None) -> str:
		now = datetime.now()
		yr = now.strftime("%Y")
		output_dir = f"{self.args.parent_path}/{yr}"
		if child_path:
			output_dir = f"{output_dir}/{child_path}"

		if mkdir:
			output_path = Path(output_dir)
			if not output_path.exists():
				self.dbgln(f"\"{output_dir}\" does not exist. making!", 1)
				# md parents as needed, don't barf if exists
				output_path.mkdir(parents=True, exist_ok=True)
		self.dbgln(f"yr=[{yr}], output_dir=[{output_dir}]", 2)
		return output_dir

	def get_jpeg_name(self, dirname: str = None) -> str:
		fname = self.args.jpeg
		if ".jpg" in fname or ".jpeg" in fname:
			pass
		else:
			self.dbgln(f"appending .jpeg", 3)
			fname += ".jpeg"

		if dirname:
			fname = dirname + "/" + fname
		self.dbgln(f"fname=[{fname}]", 2)
		return fname


if __name__ == "__main__":
	converter = HeicJpeg()
	heic_path = converter.args.input
	jpg_name = converter.get_jpeg_name(converter.get_output_dir(True, converter.args.child_path))

	converter.convert_heic_to_jpg(heic_path, jpg_name)
