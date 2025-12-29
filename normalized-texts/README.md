# Normalized text annotations for development set

Contains manually normalized versions of a sample of text rows from the development set. Used for evaluating extracting items such as the person's name from the row. 

The annotations have been done with [these scripts](https://github.com/TurkuNLP/htr-table-pipeline).

Directory contains both the json (format used by the extraction scripts in the main project) and jsonl (easier format to work with for others) versions of the same data.

## Specifics

development-set/normalized_annotations_fixed_idxs.jsonl stores a subset of table rows (n=100) from the development set with annotated texts along with annotations of the name, parish, year, and moving direction. The items (name, parish etc.) have both the original text and a normalized version annotated. The item annotations also store the source, which is either "from_row" (the item was completely stored on this row) or "from_book" (the item needed info from outside this row).

Names have been normalized to the format \[first_name middle_names last_name\]. Last names have not been inferred from adjacent rows even if it had been possible. Names that end in daughter/son (such as "Jaakontytär") have been expanded to the full form if they have been abbreviated (e.g. "Jaakont."). 

The parish item stores the parish mentioned on the row that's not the source book parish. If the row is emigration, this is the destination parish; if immigration, the source parish. The normalized parish names have been translated to Finnish where an established Finnish translation exists. 

Year stores the move year, usually inferred from the row text or book headers. 

Moving direction is either "in" or "out".
