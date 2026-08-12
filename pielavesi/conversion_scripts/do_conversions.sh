#!/bin/bash

input_dir_1="../pielavesi_muuttaneet_1875-1880_mko6"
input_dir_2="../pielavesi_muuttaneet_1881-1887_mko7"
input_dir_3="../pielavesi_muuttaneet_1881-1887_mko44-45"

instructions_1="../pielavesi_muuttaneet_1875-1880_mko6_instructions.json"
instructions_2="../pielavesi_muuttaneet_1881-1887_mko7_instructions.json"
instructions_3="../pielavesi_muuttaneet_1881-1887_mko44-45_instructions.json"

output_dir_1="../pielavesi_muuttaneet_1875-1880_mko6_conversions"
output_dir_2="../pielavesi_muuttaneet_1881-1887_mko7_conversions"
output_dir_3="../pielavesi_muuttaneet_1881-1887_mko44-45_conversions"

[ -d "$output_dir_1/xml_combined_tables" ] || mkdir -p "$output_dir_1/xml_combined_tables"
[ -d "$output_dir_1/churro" ] || mkdir "$output_dir_1/churro"
[ -d "$output_dir_1/md" ] || mkdir "$output_dir_1/md"
python3 combine_transkribus_tables.py \
    -i "$input_dir_1" \
    -o "$output_dir_1/xml_combined_tables" \
    -I "$instructions_1"
python3 convert_transkribus_to_churro.py  \
    -i "$input_dir_1/xml" \
    -o "$output_dir_1/churro" \
    -I "$instructions_1"
python3 convert_churro_to_md.py \
    -i "$output_dir_1/churro" \
    -o "$output_dir_1/md"

[ -d "$output_dir_2/xml_combined_tables" ] || mkdir -p "$output_dir_2/xml_combined_tables"
[ -d "$output_dir_2/churro" ] || mkdir "$output_dir_2/churro"
[ -d "$output_dir_2/md" ] || mkdir "$output_dir_2/md"
python3 combine_transkribus_tables.py \
    -i "$input_dir_2/" \
    -o "$output_dir_2/xml_combined_tables" \
    -I "$instructions_2"
python3 convert_transkribus_to_churro.py \
    -i "$input_dir_2/" \
    -o "$output_dir_2/churro" \
    -I "$instructions_2"
python3 convert_churro_to_md.py \
    -i "$output_dir_2/churro" \
    -o "$output_dir_2/md"

[ -d "$output_dir_3/xml_combined_tables" ] || mkdir -p "$output_dir_3/xml_combined_tables"
[ -d "$output_dir_3/churro" ] || mkdir "$output_dir_3/churro"
[ -d "$output_dir_3/md" ] || mkdir "$output_dir_3/md"
python3 combine_transkribus_tables.py \
    -i "$input_dir_3/" \
    -o "$output_dir_3/xml_combined_tables" \
    -I "$instructions_3"
python3 convert_transkribus_to_churro.py \
    -i "$input_dir_3/" \
    -o "$output_dir_3/churro" \
    -I "$instructions_3"
python3 convert_churro_to_md.py \
    -i "$output_dir_3/churro" \
    -o "$output_dir_3/md"

