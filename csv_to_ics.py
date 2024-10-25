"""CSV to ICS Converter

This script allows the user to convert a CSV file containing one event per line
into an iCalendar file (.ics).

The CSV file is expected to contain 4 columns in the following order:
- Start date as ISO 8601 formatted string (without any time information, e.g. 2024-10-03)
- End date as ISO 8601 formatted string (without any time information, e.g. 2024-10-03)
- Event name
- Optional: Event description

Note: While the description of a particular event may be empty, the column itself
must be present in the CSV file.

The iCalendar file will be written to the same location as the input CSV file, using the same
filename, just ending with .ics.
"""

import csv
import argparse
import uuid
import logging
from datetime import date
from datetime import timedelta


logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

ONE_DAY = timedelta(days=1)

# Random UUID used as namespace ID
# That way we make sure that identical events get the same VEVENT UUID.
UUID_NS = uuid.UUID('8e1072d6-0f2f-407d-b6c2-42eb1584414b')


def read_csv_file_and_generate_events(filename:str, delimiter:str = ';', contains_header:bool = True) -> list[str]:
    """Reads a CSV file and calls function create_vevent for each line.

    It makes sure that each line consists of 4 items (i.e. 4 csv columns),
    because function create_vevents expects them accordingly
    (start date, end date, event name, description).

    Returns a list of VEVENT strings.
    """

    vevents = []

    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=delimiter)
            if contains_header:
                next(csv_reader)
            for row in csv_reader:
                if len(row) != 4:
                    print(f"Skipping invalid row: {row}")
                    continue
                vevents.append(create_vevent(row))
    except FileNotFoundError:
        log.error(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        log.error(f"An error occurred: {e}")

    return vevents


def create_vevent(csv_row: list[str]) -> str:
    """Creates an ical VEVENT string from a list of strings.

    Expects the following 4 items/strings in the following order:
    - start date as ISO 8601 formatted string (without any time information, e.g. 2024-10-03)
    - end date as ISO 8601 formatted string (without any time information, e.g. 2024-10-03)
    - event name (used in VEVENT SUMMARY field)
    - optional: event description (used in VEVENT DESCRIPTION field)

    The VEVENT UUID will be based on the start date and the event name (summary).
    So the UUID will stay the same if the script is run multiple times with the same input data.
    Normally this should allow to import the resulting ics file into your calendar application
    multiple times without getting event duplicates.
    """

    start_date = date.fromisoformat(csv_row[0])

    # Unintuitively, in a VEVENT lasting one or more full days the end date must be the
    # first day _after_ the actual event span. That's why we have to add one day here.
    if csv_row[1]:
        end_date = date.fromisoformat(csv_row[1]) + ONE_DAY
    else:
        end_date = start_date + ONE_DAY

    summary = csv_row[2]
    event_uuid = uuid.uuid3(UUID_NS, f'{str(start_date)}{str(summary)}')

    # Event description is optional, we have to check if present or not
    description = None
    if csv_row[3]:
        description = f'DESCRIPTION:{csv_row[3]}\n'

    # Construct the VEVENT string
    vevent = (
        f'BEGIN:VEVENT\n'
        f'UID:{event_uuid}\n'
        f'STATUS:CONFIRMED\n'
        f'CATEGORIES:Feiertag\n'
        f'DTSTART;VALUE=DATE:{start_date.strftime("%Y%m%d")}\n'
        f'DTEND;VALUE=DATE:{end_date.strftime("%Y%m%d")}\n'
        f'SUMMARY:{summary}\n'
        f'{description if description else ""}'
        f'END:VEVENT\n'
    )

    return vevent


def write_ics_file(filename:str, vevents:list[str]) -> None:
    """Writes the given events into an ics file
    """

    header = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "CALSCALE:GREGORIAN\n"
    )

    footer = (
        "END:VCALENDAR\n"
    )

    with open(filename, 'w', encoding='utf-8') as icsfile:
        icsfile.write(header)
        icsfile.writelines(vevents)
        icsfile.write(footer)

        log.info(f"ICS file created: {filename}")


def main():
    # Handle command-line arguments
    parser = argparse.ArgumentParser(description='Read a CSV file containing full day event information and generate an ics file containing the events.')
    parser.add_argument('filename', type=str, help='The CSV file to read')
    parser.add_argument('-d', '--delimiter', default=';', type=str, help='The CSV delimiter (default: ";")')
    parser.add_argument('-n', '--noheader', action='store_true', help='The CSV does not contain a header row, i.e. the first line will not be skipped.')

    args = parser.parse_args()
    log.debug(f'Command-line arguments: {args}')

    # Read the CSV file and get a list of VEVENT items returned
    vevent_list = read_csv_file_and_generate_events(args.filename, args.delimiter, not args.noheader)
    log.info(f'{len(vevent_list)} events created')

    if len(vevent_list) > 0:
        # Write the events to an ICS file
        ics_filename = args.filename.rsplit('.', 1)[0] + '.ics'
        write_ics_file(ics_filename, vevent_list)


if __name__ == "__main__":
    main()
