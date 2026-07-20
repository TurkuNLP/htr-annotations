import argparse
from bs4.formatter import XMLFormatter
from bs4.dammit import EntitySubstitution
from pathlib import Path
from natsort import natsorted
import json
from src.transkribus_to_churro import transkribus_xmls_to_churro_xmls


argparser = argparse.ArgumentParser()
argparser.add_argument("-i", "--book_dir")
argparser.add_argument("-o", "--output_dir")
argparser.add_argument("-I", "--instructions")
args = argparser.parse_args()


book_dir = Path(args.book_dir)
output_dir = Path(args.output_dir)
instructions_file = Path(args.instructions)
transkribus_xmls = natsorted(book_dir.glob("*.xml"))

with open(instructions_file, "r") as fp:
    instructions = json.load(fp)

transkribus_xmls_to_churro_xmls(
    files=transkribus_xmls,
    output_dir=output_dir,
    instructions=instructions,
    formatter=XMLFormatter(
        indent=4,
        entity_substitution=EntitySubstitution.substitute_xml
    )
)
