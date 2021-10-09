#!/usr/bin/env python

"""
Send bulk emails to multiple destinations.

Use the email_parser.DestinationParser, email_sender.EmailSender,
email_sender.EmailMessage classes.
"""

import sys
import time
import argparse
import configparser
import logging

import email_parser
import email_sender


logging.basicConfig(level=logging.DEBUG)


def main():
    """Send bulk email to multiple destinations.

    Parse command line arguments, read configuration, parse destination file,
    customize message contents and send email.

    Sample run:
      ./send_email.py -c email.conf -m samples/master-admissions/message.txt -s "$(cat samples/master-admissions/subject)" -d samples/master-admissions/destination.csv

    Add -n for dry run:
      ./send_email.py -n -c email.conf -m samples/master-admissions/message.txt -s "$(cat samples/master-admissions/subject)" -d samples/master-admissions/destination.csv
    """

    aparser = argparse.ArgumentParser()
    aparser.add_argument('-c', '--config', nargs=1, required=True,
                        help='Configuration file')
    aparser.add_argument('-m', '--message', nargs=1, required=True,
                        help='Message file')
    aparser.add_argument('-s', '--subject', nargs=1, required=True,
                        help='Subject')
    aparser.add_argument('-d', '--destination', nargs=1, required=True,
                        help='Destination')
    aparser.add_argument('-n', '--dry', action='store_true',
                        help='Dry run')
    args = aparser.parse_args()

    # Obtain sender credentials.
    config = configparser.ConfigParser()
    config.read(args.config)

    server_name = config['server']['url']
    server_port = int(config['server']['port'])
    server_sender_name = config['sender']['name']
    server_sender_email = config['sender']['email']
    server_sender_password = config['sender']['password']
    pause = int(config['email']['pause'])
    raw_content = open(args.message[0], "r").read()
    subject = args.subject[0]

    email_from = '{} <{}>'.format(server_sender_name, server_sender_email)

    sender = email_sender.EmailSender(server_name, server_port, server_sender_email, server_sender_password)

    destination = None
    if args.destination:
        dp = email_parser.DestinationParser(args.destination[0])
        destination = dp.dests

    if args.dry:
        email_to = '{} <{}>'.format(server_sender_name, server_sender_email)
        message = email_sender.EmailMessage(raw_content, subject, email_from, email_to)
        sender.send(message)
        sys.exit(0)

    for d in destination:
        logging.debug(d)
        content = email_parser.DestinationParser.customize_content(raw_content, d)
        logging.debug(content)
        email_to = '{} {} <{}>'.format(d['firstname'], d['lastname'], d['email'])
        message = email_sender.EmailMessage(content, subject, email_from, email_to)
        sender.send(message)
        time.sleep(pause)


if __name__ == "__main__":
    main()
