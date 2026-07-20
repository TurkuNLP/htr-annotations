import argparse
from pathlib import Path
from natsort import natsorted
from src.churro_to_md import churro_xml_files_to_md_files

argparser = argparse.ArgumentParser()
argparser.add_argument("-i", "--book_dir")
argparser.add_argument("-o", "--output_dir")
args = argparser.parse_args()

book_dir = Path(args.book_dir)
output_dir = Path(args.output_dir)
churro_xmls = natsorted(book_dir.glob("*.xml"))

churro_xml_files_to_md_files(
    files=churro_xmls,
    output_dir=output_dir,
    include_frontmatter=True
)
