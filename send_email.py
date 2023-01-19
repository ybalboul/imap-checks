#!/usr/bin/python3
import smtplib
import argparse
import sys
import socket
from email.message import EmailMessage

def sendEmail(to, server, fromAddress, subject):
    try:
        message = EmailMessage()
        message.set_content("email test")
        message["Subject"] = subject
        message["From"] = fromAddress
        message["To"] = to

        s = smtplib.SMTP(server)
        s.send_message(message)
        s.quit()

        print(f'mail sent successfully\nto: {to}\nfrom: {fromAddress}\nvia: {server}')
        sys.exit(0)

    except smtplib.SMTPException as e:
        print(f'failed to send mail\nto: {to}\nfrom: {fromAddress}\nvia: {server}')
        print(e)
        sys.exit(2) 

def main():
    parser = argparse.ArgumentParser(
    description='Sends an email to be checked'
    )
    parser.add_argument('-t', '--to', nargs='?', required=True, help='email recipient')
    parser.add_argument('-s', '--server', nargs='?', required=True, help='smtp server')
    parser.add_argument('-f', '--fromAddress', nargs='?', required=True, help='email sender')
    parser.add_argument('-S', '--subject', required=False, type=str, default='email check', help='email subject')
    args = parser.parse_args()

    try:
        socket.gethostbyname(args.server)
    except:
        print(f'Hostname is unknown: {args.server}')
        sys.exit(2)

    sendEmail(args.to, args.server, args.fromAddress, args.subject.strip())

if __name__ == '__main__':
    main()
