from pathlib import Path
from bs4 import BeautifulSoup
from copy import deepcopy
from src.join_tables import join_tables


def transkribus_to_churro(transkribus: BeautifulSoup, metadata, copy=True):
    if copy:
        soup = deepcopy(transkribus)
    else:
        soup = transkribus

    metadata_tag = soup.new_tag("Metadata")
    for tag_name, tag_string in metadata.items():
        if isinstance(tag_string, list):
            for item in tag_string:
                tag = soup.new_tag(tag_name, string=str(item))
                metadata_tag.append(tag)
        else:
            tag = soup.new_tag(tag_name, string=str(tag_string))
            metadata_tag.append(tag)

    old_metadata = soup.find("Metadata")
    if old_metadata:
        old_metadata.replace_with(metadata_tag)
    else:
        if soup.contents:
            soup.contents[0].insert(0, metadata_tag)

    table_regions = list(soup.find_all("TableRegion"))
    for table_region in table_regions:
        table_region.name = "Table"
        table_region.attrs.clear()

        rows = {}
        cells = list(table_region.find_all("TableCell"))

        for cell in cells:
            cell.extract()

            row_attr = cell.get("row") or cell.get("Row")
            if row_attr is None:
                continue
            row_num = int(row_attr)

            cleaned_attrs = {}
            for k in [
                "role",
                "Role",
                "rowSpan",
                "rowspan",
                "colSpan",
                "colspan",
            ]:
                if k in cell.attrs:
                    cleaned_attrs[k.lower()] = cell.attrs[k]
            cell.attrs = cleaned_attrs

            if row_num not in rows:
                rows[row_num] = []
            rows[row_num].append(cell)

        for row_num in sorted(rows.keys()):
            table_row = soup.new_tag("TableRow")

            sorted_cells = sorted(
                rows[row_num],
                key=lambda c: int(c.get("col", 0) or c.get("Col", 0)),
            )

            for cell in sorted_cells:
                table_row.append(cell)

            table_region.append(table_row)

    all_tags = list(
        soup.find_all(["Page", "PcGts", "TextLine", "Coords", "CornerPts"])
    )
    for tag in all_tags:
        if tag.parent is None and tag.name != "PcGts":
            continue

        tag_name = tag.name

        if tag_name == "Page":
            tag.attrs.clear()

        elif tag_name == "PcGts":
            tag.name = "HistoricalDocument"
            tag.attrs = {"xmlns": "http://example.com"}

        elif tag_name == "TextLine":
            tag.name = "Line"
            text_content = tag.get_text().strip("\n")
            tag.clear()
            tag.string = text_content
            tag.attrs.clear()

        elif tag_name in ["Coords", "CornerPts"]:
            tag.decompose()

    return soup


def transkribus_xmls_to_churro_xmls(
    files: list[Path], output_dir: Path, instructions: dict, formatter=None
):

    filename_format = instructions["filename_format"]
    table_join_instructions = instructions["join_tables"]

    for file in files:
        with open(file) as fp:
            transkribus_xml = fp.read()

        page = int(
            file.stem.split(
                sep=filename_format["sep"],
                maxsplit=len(filename_format["fields"]),
            )[filename_format["fields"]["pagenr"]]
        )

        soup = BeautifulSoup(
            transkribus_xml,
            features="xml",
            preserve_whitespace_tags=[
                "Language",
                "WritingDirection",
                "PhysicalDescription",
                "Description",
                "Script",
                "Creator",
                "Created",
                "LastChange",
                "Line",
                "Unicode",
                "CornerPts",
            ],
        )

        page_table_instructions = table_join_instructions.get(str(page))
        if page_table_instructions:
            soup = join_tables(soup, instructions=page_table_instructions)

        soup = transkribus_to_churro(
            soup,
            instructions["xml_metadata"],
            False,
        )

        with open(
            output_dir / Path(file.stem + ".xml"), "w", encoding="utf-8"
        ) as fp:
            fp.write(soup.prettify(formatter=formatter))
