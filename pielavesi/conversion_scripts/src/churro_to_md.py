from pathlib import Path
from bs4 import BeautifulSoup
from copy import deepcopy
import html_to_markdown


def create_frontmatter(frontmatter_element: BeautifulSoup):
    frontmatter_dict = {}
    for el in frontmatter_element.find_all():
        key = el.name
        value = el.text.strip()

        if key in frontmatter_dict.keys():
            if type(frontmatter_dict[key]) == list:
                frontmatter_dict[key].append(value)
            else:
                frontmatter_dict[key] = [frontmatter_dict[key], value]
        else:
            frontmatter_dict[key] = value
        
    frontmatter = (
        "---\n"
        + "\n".join(
            f"{key}: {value}"
            for key, value in frontmatter_dict.items()
        )
        + "\n---"
    )


    return frontmatter


def churro_to_html(churro: BeautifulSoup, copy=True):
    if copy:
        soup = deepcopy(churro)
    else:
        soup = churro

    heading_levels = {"main": 1, "sub": 2, "running_title": 3}
    prev_valid_header = 1

    for tr in soup.find_all("TableRow"):
        tr.name = "tr"

    for c in soup.find_all("TableCell"):
        if c in ["\n", "", None]:
            continue

        elif c.attrs.get("role", None) and c.attrs.get("role") == "header":
            c.name = "th"
        else:
            c.name = "td"

    for h in soup.find_all("Heading"):
        if h.attrs.get("type", None):
            header = f"h{heading_levels[h.attrs["type"]]}"
            prev_valid_header = header
        else:
            header = prev_valid_header

        h.name = header

    for p in soup.find_all("paragraph"):
        p.name = "p"

    for ul in soup.find_all("list"):
        ul.name = "ul"

    for li in soup.find_all("item"):
        li.name = "li"

    for line in soup.find_all("Line"):
        line.parent.append(line.extract().text + "<br>")

    return soup.find()


def churro_to_md(churro_html: BeautifulSoup, include_frontmatter=False, copy=True):
    if copy:
        soup = deepcopy(churro_html)
    else:
        soup = churro_html

    metadata = soup.find("Metadata").extract()

    md = html_to_markdown.convert(str(soup)).content

    if include_frontmatter:
        frontmatter = create_frontmatter(metadata)
        md = frontmatter + "\n\n" + md

    return md


def churro_xml_files_to_md_files(
    files: list[Path],
    output_dir: Path,
    include_frontmatter=False
):
    for file in files:
        with open(file) as fp:
            churro_xml = fp.read()

        soup = BeautifulSoup(churro_xml, features="xml",
            preserve_whitespace_tags=[
                "Unicode",
                "Creator",
                "Created",
                "LastChange",
                "CornerPts",
            ]
        )

        churro_html = churro_to_html(soup, False)
        churro_md = churro_to_md(
            churro_html=churro_html,
            include_frontmatter=include_frontmatter,
            copy=False
        )

        with open(output_dir / Path(file.stem + ".md"), "w", encoding="utf-8") as fp:
            fp.write(churro_md)
