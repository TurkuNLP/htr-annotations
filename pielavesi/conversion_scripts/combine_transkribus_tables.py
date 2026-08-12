import argparse
from bs4 import BeautifulSoup
from bs4.formatter import XMLFormatter
from bs4.dammit import EntitySubstitution
from pathlib import Path
import re
import json
from src.join_tables import join_tables
from natsort import natsorted

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
table_join_instructions = instructions["join_tables"]

formatter = XMLFormatter(
    indent=4, entity_substitution=EntitySubstitution.substitute_xml
)

fixed_xmls = []
for page, original_file in enumerate(transkribus_xmls):
    with open(original_file, "r") as fp:
        transkribus_xml = fp.read()

    original_xml_tag = re.search(
        '<\\?xml version=".*?" encoding=".*?" standalone=".*?"\\?>',
        transkribus_xml,
    ).group(0)

    transkribus = BeautifulSoup(
        transkribus_xml,
        features="xml",
        preserve_whitespace_tags=[
            "Unicode",
            "Creator",
            "Created",
            "LastChange",
            "CornerPts",
        ]
    )

    page_table_instructions = table_join_instructions.get(str(page + 1), None)
    if page_table_instructions:

        transkribus =  join_tables(
            transkribus, instructions=page_table_instructions
        )
    fixed_xml = transkribus.prettify(formatter=formatter)
    fixed_xml = re.sub("<\\?xml.*?\\?>", original_xml_tag, fixed_xml)

    new_path = output_dir / f"{original_file.stem}.xml"
    with open(new_path, "w", encoding="utf-8") as fp:
        fp.write(fixed_xml)
