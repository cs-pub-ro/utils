# Bulk Email Sending

Send email to multiple destination addresses.
Email message is templated, such that each destination receives its custom message.

## Requirements

Python3 is required to run the scripts.

Access to an SMTP server is required to send email.
GMail can be used as an SMTP server.
This requires a [configuration of your Google account](https://kb.synology.com/en-global/SRM/tutorial/How_to_use_Gmail_SMTP_server_to_send_emails_for_SRM).
Note there are [limits](https://support.google.com/a/answer/166852) to the number of messages that can be sent out per day using GMail.

## How to Use

Make a copy of `email.conf.template` into `email.conf` and update with the server and sender details.
Note that only secure MSAs (*Mail Submission Agents*) are supported, i.e. using TLS/SSL (port `465`) or STARTTLS (port `587`).

Test the configuration by using the sample files in the `support/` folder:

```
```

The `-n` option triggers a *dry run*, meaning that the email is not send to any of the destinations, but to the sender.
Removing the `-n` option will send the message to the destinations.

Create the templated message file.
See the sample in `sample/master-addmissions/message.txt`.
Use `$key` for message variables, e.g. `$url`, `$id`, `$grade`.

Create the destination file as a CSV file.
See the sample in `sample/master-addmissions/destination.csv`.
Make sure to add the header with at least the `firstname`, `lastname` and `email` fields.
Add the names of the other fields named after the variables in the templated message file.

Do a test run, i.e. using the `-n` option (*dry run*) to see if the message is sent out correctly.
Then remove the `-n` option to send the messages to all destinations.

## Internals

`send_mail.py` is the top level script (with the `main()` function) that triggers the bulk message sending.
`email_parser.py` defines support classes to parse the destination file and the message template file.
`email_sender.py` defines classes to send messages using an SMTP server;
Only secure MSAs (*Mail Submission Agents*) are supported, i.e. using TLS/SSL (port `465`) or STARTTLS (port `587`).

The SMTP server is configured in the `email.conf` file.
The `email.conf` file needs to be created before everything.

Sample configuration files are in the `samples/` folder.
