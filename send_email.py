#!/usr/bin/python3
import smtplib
import argparse
import sys
import socket
import signal
import getpass
import time
from email.message import EmailMessage

def timeout(signum, frame):
    raise Exception('exceeded 10s timeout limit!') # sets exception for timeout

def sendEmail(to, server, fromAddress, subject, body, user, password, port):
    start = time.perf_counter()
    try:
        message = EmailMessage()
        message.set_content(body)
        message["Subject"] = subject
        message["From"] = fromAddress
        message["To"] = to

        if user == None:
            try:
                s = smtplib.SMTP(server, port)
                s.send_message(message)
                end = time.perf_counter()

            except:
                print(f'failed to send mail via: {server}:{port}')
                sys.exit(2)
        else:
            try:
                s = smtplib.SMTP(server, port)
                s.starttls()
                s.login(user, password)
                s.send_message(message)
                end = time.perf_counter()
            except:
                print(f'failed to send mail via: {server}:{port} with user: {user}')
                sys.exit(2)

        s.quit()
        print(f'mail sent successfully\nsubject: {subject}\nto: {to}\nfrom: {fromAddress}\nvia: {server}\nlatency: {end-start:0.4f}s')
        sys.exit(0)

    except smtplib.SMTPException as e:
        print(f'failed to send mail\nsubject: {subject}\nto: {to}\nfrom: {fromAddress}\nvia: {server}:{port}\nlatency: {end-start:0.4f}s')
        print(e)
        sys.exit(2) 

def main():
    parser = argparse.ArgumentParser(
    description='sends email'
    )
    parser.add_argument('-t', '--to', nargs='?', required=True, help='email recipient')
    parser.add_argument('-s', '--server', nargs='?', required=True, help='smtp server')
    parser.add_argument('-f', '--fromAddress', nargs='?', required=True, help='email sender')
    parser.add_argument('-S', '--subject', required=False, type=str, help='email subject')
    parser.add_argument('-b', '--body', required=False, type=str, help='email body')
    parser.add_argument('-u', '--user', action='store', nargs='?', required=False, help='user')
    parser.add_argument('-p', '--password', action='store', nargs='?', required=False, help='password')
    parser.add_argument('-P', '--port', required=False, action='store', default=25, help='server port, DEFAULT=25')
    args = parser.parse_args()

    try:
        socket.gethostbyname(args.server)
    except:
        print(f'hostname is unknown: {args.server}')
        sys.exit(2)

    if args.subject == None:
        args.subject = 'email test via {}'.format(args.server)

    if args.body == None:
        args.body = 'email test'

    if args.password == None and args.user != None:
        args.password = getpass.getpass()

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(10) # sets timeout limit to 10s
    
    try:
        sendEmail(args.to, args.server, args.fromAddress, args.subject.strip(), args.body, args.user, args.password, args.port)
    except Exception as e:
        print(e)
        sys.exit(2)

if __name__ == '__main__':
    main()
