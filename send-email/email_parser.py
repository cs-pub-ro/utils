"""
Implement parsing of content / configuration files for sending emails.

DestinationParser is a class that parses a CSV file.
It reads the header as keys and the rows as values.
Three keys are mandatory: `firstname`, `lastname`, `email`.
The other keys are used to customize a templated email message.

MessageMapping is a dictionary-like class (i.e. it defines the __getitem__()
method. It maps keys in the destination CSV file to values.
It is used to construct the customized email message from the templated
version.
"""

import sys
import csv
import argparse
import string


class MessageMapping:
    """Create a mapping to be used by the string Template class.

    This is used to generate a custom message according to fields
    read from a configuration file with email destinations and custom
    email message fields.
    """

    def __init__(self, fields):
        self.fields = fields

    def __getitem__(self, key):
        return self.fields[key]


class DestinationParser:
    """Parse CSV file with destination information: name, email, message
    values.

    The first line in the the CSV file is expected to store the header.
    It's mandatory that three items in the header are `firstname`, `lastname`
    and `email`. The other items in the header are keys that will be replaced
    in the message with the actual values.
    """

    def __init__(self, fname):
        self.dests = []

        with open(fname) as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)
            if 'firstname' not in header or 'lastname' not in header \
                    or 'email' not in header:
                        raise KeyError("Missing keys in CSV header.")

            for row in reader:
                d = {
                        'firstname': '',
                        'lastname': '',
                        'email': '',
                        'fields': {},
                        }
                for k, v in zip(header, row):
                    if k == 'firstname' or k == 'lastname' or k == 'email':
                        d[k] = v
                    else:
                        d['fields'][k] = v
                self.dests.append(d)

    def print(self):
        for d in self.dests:
            print("{} {} <{}> ({})".format(
                d['firstname'],
                d['lastname'],
                d['email'],
                d['fields']))


    def customize_content(raw_content, d):
        """Customize content according to destination key-value mapping.

        `raw_content` is the message with placeholder for keys.
        Replace all occurrances of `$key` in `raw_content` with `value`.
        i.e. In case of `"name": "George"` mapping, replace `$name` with
        `George.
        Keys and values are extracted from the d['fields'] dictionary.
        """
        mm = MessageMapping(d['fields'])
        return string.Template(raw_content).substitute(mm)


def main():
    """Test DestinationParser class.

    Pass path to destination CSV file and to message file.
    Create DestinationParser object.
    Print read objects.
    Print customized message (with $key entries substituted).

    Sample run:
      python email_parser.py -d samples/master-admissions/destination.csv -m samples/master-admissions/message.txt
    """

    aparser = argparse.ArgumentParser()
    aparser.add_argument('-d', '--destination', nargs=1, required=False,
                        help='Destination file')
    aparser.add_argument('-m', '--message', nargs=1, required=False,
                        help='Message file')
    args = aparser.parse_args()

    if args.destination:
        dp = DestinationParser(args.destination[0])
        dp.print()
    if args.message:
        raw_content = open(args.message[0], "r").read()
        print("\n=== Customized message:\n")
        print(DestinationParser.customize_content(raw_content, dp.dests[0]))


if __name__ == "__main__":
    main()
