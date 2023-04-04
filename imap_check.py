#!/usr/bin/python3
import imaplib
import email
import datetime
import sys
import argparse
import getpass
import socket
import signal
import re
from email.utils import parsedate_tz, mktime_tz

def timeout(signum, frame):
    raise Exception('exceeded 10s timeout limit!') # sets exception for timeout

def externalVerification(imap, user, password, delete, time, port, fromAddress, subject, regexStr, regexCheck):
    try:
        mail = imaplib.IMAP4_SSL(imap, port)
    except:
        print(f'failed to connect to: {imap}:{port}')
        sys.exit(2)
    try: 
        mail.login(user, password)
    except:
        print(f'failed to authenticate via {user}')
        sys.exit(2)
   
    # filters inbox by sender
    mail.select('Inbox', readonly=False)
    res, data = mail.search(None, 'FROM', fromAddress)
    ids = data[0]
    mailList = ids.split()
    externalStatus = False

    if len(mailList) == 0:
        print(f'no mail has been found matching your criteria!\nsubject: {subject}\nfrom: {fromAddress}\nuser: {user}\nserver: {imap}')
        sys.exit(2)

    for i in mailList:
        res, data = mail.fetch(i, '(RFC822)')
        for x in data:
            if isinstance(x, tuple):
                part = x[1].decode('utf-8')
                msg = email.message_from_string(part)
                bodyPayload = msg.get_payload(decode=True) # recieves body of email
                bodyEmail = bodyPayload.decode()
                subjectEmail = msg['Subject']
                date = msg['Date']
                to = msg['To']
                fromAddress = msg['From']
                
                # if something in the body of the email matches your regex search, we will later exit 0, 1, or 2 depending on if we are searching for something considered bad or good
                regexExitStatus = None
                if not regexStr == None and regexCheck == True:
                    if re.search(regexStr, bodyEmail): # searching for good
                        regexExitStatus = 0
                    elif re.search(regexStr, bodyEmail) == None: # can't find
                        regexExitStatus = 1
                elif not regexStr == None and regexCheck == False:
                    if re.search(regexStr, bodyEmail): # searching for bad
                        regexExitStatus = 2
                    elif re.search(regexStr, bodyEmail) == None: # can't find
                        regexExitStatus = 1

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

    return externalStatus, date, to, fromAddress, subjectEmail, len(mailList), regexExitStatus


def main():
    parser = argparse.ArgumentParser(
        description='checks to see if email is present'
    )
    parser.add_argument('-s', '--server', required=True, nargs='?', action='store', help='imap server')
    parser.add_argument('-u', '--user', required=True, nargs='?', action='store', help='imap user')
    parser.add_argument('-p', '--password', required=False, nargs='?', action='store', help='imap password, password prompt will appear by default')
    parser.add_argument('-d', '--delete', required=False, action='store_true', help='deletes emails filtered') 
    parser.add_argument('-t', '--time', required=False, action='store', default=5, help='specifies time(minutes) delta, DEFAULT=5') 
    parser.add_argument('-P', '--port', required=False, action='store', default=993, help='server port, DEFAULT=993')
    parser.add_argument('-f', '--fromAddress', required=True, action='store', help='filters email from')
    parser.add_argument('-S', '--subject', required=True, action='store', type=str, help='filters email subject')
    parser.add_argument('-r', '--regexGood', required=False, action='store', type=str, help='regex for body, exits happy if found')
    parser.add_argument('-R', '--regexBad', required=False, action='store', type=str, help='regex for body, exits unhappy if found')

    args = parser.parse_args()

    # checks if you passed a password as an argurment
    
    try:
        socket.gethostbyname(args.server)
    except:
        print(f'Hostname is unknown: {args.server}')
        sys.exit(2)

    password = args.password
    if password == None:
        password = getpass.getpass()

    regexCheck = None
    regexStr = None
    if not args.regexGood == None:
        regexCheck = True # we are checking for something good, so we can exit happy (good exit (0))
        regexStr = args.regexGood
    elif not args.regexBad == None:
        regexCheck = False # we are checking for a error, so we can exit upset (critical exit(2))
        regexStr = args.regexBad
    
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(10) # sets timeout limit to 10s

    try: 
        status, date, to, fromAddress, subject, amountFound, regexExitStatus = externalVerification(args.server, args.user, password, args.delete, args.time, args.port, args.fromAddress, args.subject.strip(), regexStr, regexCheck)
    except Exception as e:
        print(e)
        sys.exit(2)

    if status:
        if regexExitStatus == 0:
            print(f'email found!\nregex search: "{regexStr}", was found exiting with 0!\nsubject: {subject}\nto: {to}\nfrom: {fromAddress}\ndate: {date}\nserver: {args.server}\namount found: {amountFound}\ndeletion: {args.delete}') 
            sys.exit(0) # mail found with good regex result
        elif regexExitStatus == 2:
            print(f'email found!\nregex search: "{regexStr}", was found exiting with 2!\nsubject: {subject}\nto: {to}\nfrom: {fromAddress}\ndate: {date}\nserver: {args.server}\namount found: {amountFound}\ndeletion: {args.delete}') 
            sys.exit(2) # mail found with bad regex result
        elif regexExitStatus == 1:
            print(f'email found!\nregex search: "{regexStr}", was not found, exiting with 1!\nsubject: {subject}\nto: {to}\nfrom: {fromAddress}\ndate: {date}\nserver: {args.server}\namount found: {amountFound}\ndeletion: {args.delete}') 
            sys.exit(1) # mail found but regex not found
        else:
            print(f'email found!\nregex search: {regexStr}\nsubject: {subject}\nto: {to}\nfrom: {fromAddress}\ndate: {date}\nserver: {args.server}\namount found: {amountFound}\ndeletion: {args.delete}') 
    else:
            print(f'failed to find specified mail with in last {args.time} minutes!\nsubject: {subject}\nto: {to}\nfrom: {fromAddress}\nserver: {args.server}')
            sys.exit(2) # mail not found

if __name__ == '__main__':
    main()
