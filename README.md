# nagios-imap-checks
Two scripts made at work for Nagios, which send email to an external mail address (e.g. gmail) which is set to autoforward to an internal mail address, which is then checked with the second script, verifying external mail is working. Both scripts have mulitiple parameters allowing you to change what server you are sending from/receiving, who is sending the email, etc. Which allows the script to be expanded further from external email verification checks (e.g. various internal checks).

sending an email
> ./send_email.py [REQUIRED] -t [to] -f [from] -s [server] [OPTIONAL] -S [subject] -b [body] -u [user] -P [port] -p [password]

verifying email has been received 
> ./imap_check.py [REQUIRED] -s [server] -u [user] -f [from] -S [subject] [OPTIONAL] -p [password] -d [delete] -t [time delta] 
