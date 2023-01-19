#!/usr/bin/python3
import imaplib
import email
import datetime
import sys
import argparse
import getpass
import socket
from email.utils import parsedate_tz, mktime_tz

def externalVerification(imap, user, password, delete, time, port, filter, subject):
    try:
        mail = imaplib.IMAP4_SSL(imap, port)
        try: 
            mail.login(user, password)
        except:
            print(f'Failed to authenticate via {user}')
            sys.exit(2)
    except:
        print(f'Failed to connect to: {imap}:{port}')
        sys.exit(2)

    # filters inbox by sender
    mail.select('Inbox', readonly=False)
    res, data = mail.search(None, 'FROM', filter)
    ids = data[0]
    mailList = ids.split()
    externalStatus = False

    for i in mailList:
        res, data = mail.fetch(i, '(RFC822)')
        for x in data:
            if isinstance(x, tuple):
                part = x[1].decode('utf-8')
                msg = email.message_from_string(part)
                subjectEmail = msg['Subject']
                date = msg['Date']
                to = msg['To']
                fromAddress = msg['From']

                # marks current email for deletion
                if delete:
                    mail.store(i, '+FLAGS', '\\Deleted')

                # current time in epoch
                currentTime = datetime.datetime.now() 
                currentTimeEpoch = currentTime.timestamp()

                # receives mail time and covnerts to epoch time
                parsedDate = parsedate_tz(date)
                receivedTimeEpoch = mktime_tz(parsedDate)

                # time range converted to epoch 
                timeDelta = currentTime - datetime.timedelta(minutes=int(time))
                timeDeltaEpoch = int(timeDelta.timestamp())

                if subject in subjectEmail:
                        if receivedTimeEpoch <= currentTimeEpoch and receivedTimeEpoch > timeDeltaEpoch:
                            externalStatus = True
    if delete:
        mail.expunge()

    mail.close()
    mail.logout()
    return externalStatus, date, to, fromAddress, subjectEmail

def main():
    parser = argparse.ArgumentParser(
        description='checks internal email to verify external email is working'
    )
    parser.add_argument('-s', '--server', required=True, nargs='?', action='store', help='imap server')
    parser.add_argument('-u', '--user', required=True, nargs='?', action='store', help='imap user login')
    parser.add_argument('-p', '--password', required=False, nargs='?', action='store', help='imap password')
    parser.add_argument('-d', '--delete', required=False, action='store_true', help='deletes all emails searched') 
    parser.add_argument('-t', '--time', required=False, action='store', default=5, help='specifies time(minutes) delta, DEFUALT=5') 
    parser.add_argument('-P', '--port', required=False, action='store', default=993, help='port for address, DEFUALT=993')
    parser.add_argument('-f', '--fromAddress', required=True, action='store', help='filters email from')
    parser.add_argument('-S', '--subject', required=False, action='store', nargs='?', type=str, default='email check', help='filters email subject, DEFUALT=email check')
    args = parser.parse_args()

    # checks if you passed a password as an argurment
    password = args.password
    if password == None:
        password = getpass.getpass()
    
    try:
        socket.gethostbyname(args.server)
    except:
        print(f'Hostname is unknown: {args.server}')
        sys.exit(2)
        
    status, date, to, fromAddress, subject = externalVerification(args.server, args.user, password, args.delete, args.time, args.port, args.fromAddress, args.subject.strip())

    if status:
        print(f'external mail is up, email found:\nsubject: {subject}\nto: {to}\nfrom: {fromAddress}\ndate: {date}\nserver: {args.server}\ndeletion: {args.delete}') 
        sys.exit(0)
    else:
        print(f'external mail is down, failed to find specified mail with in last {args.time} minutes:\nsubject: {subject}\nto: {to}\nfrom: {fromAddress}\nserver: {args.server}')
        sys.exit(2) # external mail down

if __name__ == '__main__':
    main()
