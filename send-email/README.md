# Bulk Email Sending

Send email to mutiple destination addreeses.
Email message is templated, such that each destination receives its custom message.

Make a copy of `email.conf.template` into `email.conf` and update with the server and sender details.

Sample runs:
```
./send_email.py -c email.conf -m SEERC2021_resources_message.txt -t SEERC2020-2021_teams.csv -s "[ACM] ICPC SEERC 2021 General Information"
./send_email.py -c email.conf -m SEERC2021_reminder_zoom_connect_message.txt -s 'ACM ICPC SEERC 2021: Activities for Saturday, May 22, 2021' -t SEERC2020-2021_teams.csv --accounts SEERC2020-2021_accounts_trial.csv
```
