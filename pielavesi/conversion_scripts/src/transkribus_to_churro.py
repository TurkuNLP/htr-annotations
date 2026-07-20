from pathlib import Path
from bs4 import BeautifulSoup
from copy import deepcopy


def combine_tables_vertically(
    table_1, table_2, table_1_is_header=False, copy=True
):
    if copy:
        t1 = deepcopy(table_1)
        t2 = deepcopy(table_2)
    else:
        t1 = table_1
        t2 = table_2

    t1_cells = t1.find_all("TableCell")
    t2_cells = t2.find_all("TableCell")

    if table_1_is_header:
        for tc in t1_cells:
            tc["role"] = "header"

    max_t1_row = max(int(tc.attrs.get("row", 0)) for tc in t1_cells)
    for tc in t2_cells:
        tc["row"] = str(int(tc["row"]) + max_t1_row + 1)

    t1.append(t2)

    return t1


def combine_tables_horizontally(
    table_1, table_2, soup, n_empty_cols_in_middle=0, copy=True
):
    if copy:
        t1 = deepcopy(table_1)
        t2 = deepcopy(table_2)
    else:
        t1 = table_1
        t2 = table_2

    new_rows = []

    for tc in t1.find_all("TableCell"):
        row = int(tc.attrs["row"])
        while row >= len(new_rows):
            new_rows.append([])

        new_rows[row].append(tc)

    for _ in range(n_empty_cols_in_middle):
        for i, row in enumerate(new_rows):
            last_col = int(new_rows[i][-1].attrs["col"])
            new_cell = soup.new_tag(
                "TableCell",
                attrs={
                    "col": str(last_col + 1),
                    "colSpan": "1",
                    "rowSpan": "1",
                    "row": str(i),
                },
            )
            row.append(new_cell)

    for tc in t2.find_all("TableCell"):
        row = int(tc.attrs["row"])

        while row >= len(new_rows):
            new_rows.append([])

        if new_rows[row]:
            last_col = max(int(cell["col"]) for cell in new_rows[row])
        else:
            last_col = -1

        t2_row = [
            cell
            for cell in t2.find_all("TableCell")
            if int(cell["row"]) == row
        ]
        min_col = min(int(cell["col"]) for cell in t2_row)

        offset = last_col + 1 - min_col

        tc["col"] = str(int(tc["col"]) + offset)
        new_rows[row].append(tc)

    new_table = soup.new_tag("TableRegion")
    for row in new_rows:
        row = sorted(row, key=lambda cell: int(cell["col"]))
        for cell in row:
            new_table.append(cell)

    return new_table


def transkribus_to_churro(transkribus: BeautifulSoup, metadata, copy=True):
    if copy:
        soup = deepcopy(transkribus)
    else:
        soup = transkribus

    metadata_tag = soup.new_tag("Metadata")
    for tag_name, tag_string in metadata.items():
        if type(tag_string) == list:
            for item in tag_string:
                tag = soup.new_tag(tag_name, string=item)
        else:
            tag = soup.new_tag(tag_name, string=tag_string)
        metadata_tag.append(tag)

    soup.find("Metadata").replace_with(metadata_tag)

    for tag in soup.find_all(
        ["Page", "PcGts", "TableRegion", "TextLine", "Coords", "CornerPts"]
    ):
        tag_name = tag.name

        if tag_name == "Page":
            tag.attrs.clear()

        if tag_name == "PcGts":
            tag.name = "HistoricalDocument"
            tag.attrs = {"xlmns": "http://example.com/historicaldocument"}

        if tag_name == "TextLine":
            tag.name = "Line"
            tag.string = tag.text.strip("\n")
            tag.attrs.clear()

        if tag_name == "Coords" or tag_name == "CornerPts":
            tag.decompose()

        if tag_name == "TableRegion":
            tag.name = "Table"
            tag.attrs.clear()

            rows = {}

            for cell in tag.find_all("TableCell"):
                cell = cell.extract()
                row = int(cell["row"])

                cell.attrs = {
                    k.lower(): cell.attrs[k]
                    for k in ["role", "rowSpan"]
                    if k in cell.attrs
                }

                if not rows.get(row):
                    rows[row] = []

                rows[row].append(cell)

            for row_num in sorted(rows):
                table_row = soup.new_tag("TableRow")

                for cell in rows[row_num]:
                    table_row.append(cell)

                tag.append(table_row)

    return soup


def transkribus_xml_combine_tables(
    transkribus: BeautifulSoup, table_join_instructions, copy=True
):
    if copy:
        soup = deepcopy(transkribus)
    else:
        soup = transkribus

    tables = list(soup.find_all("TableRegion"))

    for join in table_join_instructions:
        direction = join[0]
        table_1_idx = join[1]
        table_2_idx = join[2]
        extra_instruction = join[3]

        table_1 = tables[table_1_idx]
        table_2 = tables[table_2_idx]

        if direction == "vertical":
            combined = combine_tables_vertically(
                table_1,
                table_2,
                table_1_is_header=extra_instruction,
                copy=True,
            )
        elif direction == "horizontal":
            combined = combine_tables_horizontally(
                table_1,
                table_2,
                soup,
                n_empty_cols_in_middle=extra_instruction,
                copy=True,
            )

        table_1.replace_with(combined)
        table_2.decompose()

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
                # Metadata
                "Language",
                "WritingDirection",
                "PhysicalDescription",
                "Description",
                "Script",
                "Creator",
                "Created",
                "LastChange",
                # Other
                "Line",
                "Unicode",
                "CornerPts",
            ],
        )
        soup = transkribus_xml_combine_tables(
            soup, table_join_instructions.get(str(page), []), False
        )

        soup = transkribus_to_churro(
            soup,
            instructions["xml_metadata"],
            False,
        )

        with open(
            output_dir / Path(file.stem + ".xml"), "w", encoding="utf-8"
        ) as fp:
            fp.write(soup.prettify(formatter=formatter))
