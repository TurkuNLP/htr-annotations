import json
import argparse
import os
from pathlib import Path

def clean_image_name(image_path):
    # Get the basename without path
    basename = os.path.basename(image_path)
    # Remove the hash component (everything before the first dash)
    return basename.split('-', 1)[1] if '-' in basename else basename

def transform_entry(entry):
    # Parse comma-separated years into lists of integers
    def parse_years(years_str):
        if not years_str:
            return []
        return [year.strip() for year in years_str.split(',') if year.strip()]

    # Create new entry with required fields
    new_entry = {
        'image': clean_image_name(entry['image']),
        'right_years': parse_years(entry.get('right_years', '')),
        'left_years': parse_years(entry.get('left_years', '')),
        'year_rectangles': entry.get('label', [])
    }
    return new_entry

def main():
    parser = argparse.ArgumentParser(description='Clean and transform JSON data')
    parser.add_argument('input_file', help='Input JSON file path')
    args = parser.parse_args()

    # Read input JSON file
    with open(args.input_file, 'r') as f:
        data = json.load(f)

    # Transform each entry and output as JSONL
    for entry in data:
        transformed = transform_entry(entry)
        print(json.dumps(transformed))

if __name__ == '__main__':
    main()
