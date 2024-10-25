# CSV to ICS Converter

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

## Usage

```
$ python3 csv_to_ics.py [-h] [-d DELIMITER] [-n] filename

Read a CSV file containing full day event information and generate an ics file containing the events.

positional arguments:
  filename              The CSV file to read

options:
  -h, --help            show this help message and exit
  -d DELIMITER, --delimiter DELIMITER
                        The CSV delimiter (default: ";")
  -n, --noheader        The CSV does not contain a header row, i.e. the first line will not be skipped.
```

## Input Example

The CSV file must look similar to this one:

```
START;END;NAME;DESCRIPTION
2024-10-03;;German Unity Day;
2024-10-31;;Reformation Day;
2024-10-21;2024-11-03;Autumn Holidays;
```

## Motivation

Sometimes one needs to add lots of events to a Calendar. Unfortunately, with most Calendar applications such a task is quite cumbersome.
Bulk editing the events right in an iCalendar file is very error prone as well.

This is where spreadsheet applications come in very handy. One can edit all events quite easily, especially if there are repeating or similar event names.

All that is left to do is to export the spreadsheet as a CSV file and convert it to an iCalendar file using this script. Then it can be imported into the Calendar application of choice.
