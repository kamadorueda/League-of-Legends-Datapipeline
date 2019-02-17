#!/usr/bin/env python3

import os
import csv
import shutil
import progressive

if os.path.isdir("data"):
    shutil.rmtree("data")

if not os.path.isdir("data"):
    os.mkdir("data")

for table_name in os.listdir("records"):
    with open(f"data/{table_name}.csv", "w") as csv_file:
        writer = csv.writer(csv_file, **progressive.format)
        writer.writerow(
            progressive.read_schema_from_file(table_name[0:-4]))
        for record in progressive.read_records_from_file(table_name[0:-4]):
            writer.writerow(record)
