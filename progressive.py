import os
import csv

format = {
    "delimiter": ",",
    "quotechar": "\"",
    "quoting": csv.QUOTE_ALL,
}

def read_schema_from_file(table_name):
    with open(f"schemas/{table_name}.schema.csv", "r") as schema_file:
        return next(csv.reader(schema_file, **format))


def read_records_from_file(table_name):
    with open(f"records/{table_name}.csv", "r") as record_file:
        for row in csv.reader(record_file, **format):
            yield row


def write_schema_to_file(table_name, schema):
    try:
        with open(f"schemas/{table_name}.schema.csv", "w") as schema_file:
            csv.writer(schema_file, **format).writerow(schema)
    except FileNotFoundError:
        # create the path
        os.makedirs(f"schemas")
        # retry
        write_schema_to_file(table_name, schema)


def write_record_to_file(table_name, record):
    # read schema from file if it exists
    try:
        schema = read_schema_from_file(table_name)
    except FileNotFoundError:
        schema = []

    # write record to file
    try:
        with open(f"records/{table_name}.csv", "a") as csvfile:
            csv.DictWriter(csvfile, schema, **format).writerow(record)
    except FileNotFoundError:
        # create paths if it not exist
        os.makedirs(f"records")
        # retry
        write_record_to_file(table_name, record)
    except ValueError:
        # add new fields to the schema and retry
        for field in record:
            if not field in schema:
                schema.append(field)
        # retry
        write_schema_to_file(table_name, schema)
        write_record_to_file(table_name, record)
