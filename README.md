# nagios-email-checks
Two scripts made at work for Nagios, which send email to an external mail address (gmail for ex.) which is set to autoforward to an internal mail address, which is then checked with the second script, verifying external mail is working. Both scripts have mulitiple parameters allowing you to change what server you are sending from/receiving, who is sending the email, etc. Which allows the script to be expanded further from external email verification checks.

sending an email
> ./send_email.py -t [email address sending to] -f [email being sent from] -s [smtp server sending via] [OPTIONAL] -S [custom email subject, by default "email check"]

verifying email has been received 
> ./external_email_check.py -u [user] -f [filter inbox via from] -s [mail server checking] [OPTIONAL] -t [time range to check for, default is 5 minutes], -P [port for server, default is 993] -S [email subject, default "email check"] -d [deletes found emails] -p [password to login, if not called getpass will prompt for user password]
