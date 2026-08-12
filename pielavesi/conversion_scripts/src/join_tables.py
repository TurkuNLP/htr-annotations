from copy import deepcopy


def _cells(table, cell_tag):
    return table.find_all(cell_tag, recursive=False) or table.find_all(
        cell_tag
    )


def _extent(cell, pos_attr, span_attr):
    pos = int(cell.get(pos_attr, 0))
    span = int(cell.get(span_attr, 1))
    return pos + span


def _table_width(cells, col_attr, colspan_attr):
    return max((_extent(c, col_attr, colspan_attr) for c in cells), default=0)


def _table_height(cells, row_attr, rowspan_attr):
    return max((_extent(c, row_attr, rowspan_attr) for c in cells), default=0)


def _new_table_like(soup, template):
    return soup.new_tag(template.name, attrs=dict(template.attrs))


def _parse_points(points_str):
    pts = []
    for pair in points_str.split():
        x_str, y_str = pair.split(",")
        pts.append((float(x_str), float(y_str)))
    return pts


def _table_bbox(table, coords_tag, points_attr):
    coords = table.find(coords_tag, recursive=False)
    if coords is None or not coords.get(points_attr):
        return None
    pts = _parse_points(coords[points_attr])
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def _union_bbox(bbox_a, bbox_b):
    if bbox_a is None:
        return bbox_b
    if bbox_b is None:
        return bbox_a
    min_x = min(bbox_a[0], bbox_b[0])
    min_y = min(bbox_a[1], bbox_b[1])
    max_x = max(bbox_a[2], bbox_b[2])
    max_y = max(bbox_a[3], bbox_b[3])
    return (min_x, min_y, max_x, max_y)


def _bbox_to_points(bbox):
    min_x, min_y, max_x, max_y = bbox

    def fmt(n):
        return str(int(n)) if float(n).is_integer() else str(n)

    corners = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in corners)


def _table_corners(table, coords_tag, points_attr):
    coords = table.find(coords_tag, recursive=False)
    if coords is None or not coords.get(points_attr):
        return None
    pts = _parse_points(coords[points_attr])
    if len(pts) != 4:
        return None
    return pts


def _fmt_point(pt):
    x, y = pt

    def fmt(n):
        return str(int(n)) if float(n).is_integer() else str(n)

    return f"{fmt(x)},{fmt(y)}"


def _points_from_corners(corners):
    return " ".join(_fmt_point(p) for p in corners)


def _set_coords_bbox_fallback(
    soup, result, table_a, table_b, coords_tag, points_attr
):
    bbox = _union_bbox(
        _table_bbox(table_a, coords_tag, points_attr),
        _table_bbox(table_b, coords_tag, points_attr),
    )
    if bbox is None:
        return
    coords = soup.new_tag(coords_tag)
    coords[points_attr] = _bbox_to_points(bbox)
    result.insert(0, coords)


def _set_coords_horizontal(
    soup, result, table_a, table_b, coords_tag, points_attr
):
    corners_a = _table_corners(table_a, coords_tag, points_attr)
    corners_b = _table_corners(table_b, coords_tag, points_attr)
    if corners_a is None or corners_b is None:
        _set_coords_bbox_fallback(
            soup, result, table_a, table_b, coords_tag, points_attr
        )
        return
    top_left, _, _, bottom_left = corners_a
    _, top_right, bottom_right, _ = corners_b
    coords = soup.new_tag(coords_tag)
    coords[points_attr] = _points_from_corners(
        [top_left, top_right, bottom_right, bottom_left]
    )
    result.insert(0, coords)


def _set_coords_vertical(
    soup, result, table_a, table_b, coords_tag, points_attr
):
    corners_a = _table_corners(table_a, coords_tag, points_attr)
    corners_b = _table_corners(table_b, coords_tag, points_attr)
    if corners_a is None or corners_b is None:
        _set_coords_bbox_fallback(
            soup, result, table_a, table_b, coords_tag, points_attr
        )
        return
    top_left, top_right, _, _ = corners_a
    _, _, bottom_right, bottom_left = corners_b
    coords = soup.new_tag(coords_tag)
    coords[points_attr] = _points_from_corners(
        [top_left, top_right, bottom_right, bottom_left]
    )
    result.insert(0, coords)


def _empty_cell(soup, cell_tag, row_attr, col_attr, row, col):
    cell = soup.new_tag(cell_tag)
    cell[row_attr] = str(row)
    cell[col_attr] = str(col)
    return cell


def _join_horizontal(
    soup,
    table_a,
    table_b,
    gap,
    cell_tag,
    row_attr,
    col_attr,
    rowspan_attr,
    colspan_attr,
    coords_tag,
    points_attr,
):
    cells_a = _cells(table_a, cell_tag)
    cells_b = _cells(table_b, cell_tag)
    width_a = _table_width(cells_a, col_attr, colspan_attr)
    height_a = _table_height(cells_a, row_attr, rowspan_attr)
    height_b = _table_height(cells_b, row_attr, rowspan_attr)
    shift = width_a + gap

    result = _new_table_like(soup, table_a)
    _set_coords_horizontal(
        soup, result, table_a, table_b, coords_tag, points_attr
    )

    for cell in cells_a:
        result.append(deepcopy(cell))

    for row in range(max(height_a, height_b)):
        for g in range(gap):
            result.append(
                _empty_cell(
                    soup, cell_tag, row_attr, col_attr, row, width_a + g
                )
            )

    for cell in cells_b:
        new_cell = deepcopy(cell)
        new_cell[col_attr] = str(int(cell.get(col_attr, 0)) + shift)
        result.append(new_cell)

    return result


def _join_vertical(
    soup,
    table_a,
    table_b,
    header,
    cell_tag,
    row_attr,
    col_attr,
    rowspan_attr,
    colspan_attr,
    role_attr,
    header_value,
    coords_tag,
    points_attr,
):
    cells_a = _cells(table_a, cell_tag)
    cells_b = _cells(table_b, cell_tag)
    height_a = _table_height(cells_a, row_attr, rowspan_attr)
    shift = height_a

    result = _new_table_like(soup, table_a)
    _set_coords_vertical(
        soup, result, table_a, table_b, coords_tag, points_attr
    )

    for cell in cells_a:
        new_cell = deepcopy(cell)
        if header:
            new_cell[role_attr] = header_value
        result.append(new_cell)

    for cell in cells_b:
        new_cell = deepcopy(cell)
        new_cell[row_attr] = str(int(cell.get(row_attr, 0)) + shift)
        result.append(new_cell)

    return result


def join_tables(
    soup,
    instructions,
    table_tag="TableRegion",
    cell_tag="TableCell",
    row_attr="row",
    col_attr="col",
    rowspan_attr="rowSpan",
    colspan_attr="colSpan",
    role_attr="role",
    header_value="header",
    coords_tag="Coords",
    points_attr="points",
):
    tables = soup.find_all(table_tag)

    for op, i, j, param in instructions:
        idx_a, idx_b = i, j
        table_a, table_b = tables[idx_a], tables[idx_b]

        if op == "horizontal":
            joined = _join_horizontal(
                soup,
                table_a,
                table_b,
                param,
                cell_tag,
                row_attr,
                col_attr,
                rowspan_attr,
                colspan_attr,
                coords_tag,
                points_attr,
            )
        elif op == "vertical":
            joined = _join_vertical(
                soup,
                table_a,
                table_b,
                param,
                cell_tag,
                row_attr,
                col_attr,
                rowspan_attr,
                colspan_attr,
                role_attr,
                header_value,
                coords_tag,
                points_attr,
            )
        else:
            raise ValueError(f"unknown join type: {op}")

        table_a.replace_with(joined)
        table_b.decompose()

        tables[idx_a] = joined
        del tables[idx_b]

    return soup
