#!/usr/bin/python
"""
send email using smtp

default:
    sent email from mclab_speech@qq.com to bily.lee@qq.com without attachment

TODO:
    1. maybe try to send formatted html could be a good idea

Feature:
    * support pipe or redirection as long as you put a dash('-') as placeholder for message
    * support email attachment
    * get a beautiful notify after mail is successfully sent

usage:
    1. prepare an email acount that provides smtp service(like qq or gmail)
    2. store the password in a text file, the password should be encoded by base64.b64encode function
      import base64
      base64.b64encode("password")
    3. you can modify the default value of the sender, recipient and the password file location
    3. send the email
      a. with default sender and recipient
        ./sendmail.py "greetings!"
      b. with the specified sender and recipient
        ./sendmail.py -se mclab_speech@qq.com -p /etc/mail.password -t bily.lee@qq.com "message body"
      c. with attachment
        ./sendmail.py -a sendmail "attached with the sendmail script"

"""
import os, re
import sys

# Import smtplib for the actual sending function
import smtplib

# For guessing MIME type based on file name extension
import mimetypes

# parse argument
import argparse

# use stdin
import fileinput

#from email.mime.image import MIMEImage
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.MIMEText import MIMEText

def parse_email_address(email_address):
    sys.stderr.write("parsing the email address to get the smtp server...\n")
    parts = email_address.split("@")
    if len(parts) != 2:
        # it should have the pattern of XXXX@XXXX.XXXX
        raise Exception("the pattern of the email address should be XXXX@XXXX.XXXX")
    parts = parts[1].split(".")
    server_name = parts[0]
    if server_name == "gmail":
        SMTP_SERVER = "smtp.gmail.com"
    elif server_name == "163":
        SMTP_SERVER = "smtp.163.com"
    elif server_name == "qq":
        SMTP_SERVER = "smtp.qq.com"
    else:
        sys.stderr.write( "the server is not defined, you should add it in the code\n")
    sys.stderr.write("the server is: " + SMTP_SERVER + "\n")
    return SMTP_SERVER

def parse_attachment(path):
    if not os.path.isfile(path):
        raise Exception("the attachment path is not exist!")    
    # Guess the content type based on the file's extension.  Encoding
    # will be ignored, although we should check for simple things like
    # gzip'd or compressed files.
    ctype, encoding = mimetypes.guess_type(path) 
    if ctype is None or encoding is not None:
    # No guess could be made, or the file is encoded (compressed), so
    # use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
	fp = open(path)
	# Note: we should handle calculating the charset
	msg = MIMEText(fp.read(), _subtype=subtype)
	fp.close()
    elif maintype == 'image':
	fp = open(path, 'rb')
	msg = MIMEImage(fp.read(), _subtype=subtype)
	fp.close()
    elif maintype == 'audio':
	fp = open(path, 'rb')
	msg = MIMEAudio(fp.read(), _subtype=subtype)
	fp.close()
    else:
	fp = open(path, 'rb')
	msg = MIMEBase(maintype, subtype)
	msg.set_payload(fp.read())
	fp.close()
	# Encode the payload using Base64
	encoders.encode_base64(msg)
    # Set the filename parameter
    import ntpath # this module can handle all paths on all platforms
    head,tail = ntpath.split(path)
    filename = tail or ntpath.basename(path) # handle path which ends with a slash
 
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    return msg

def main():
    parser = argparse.ArgumentParser(description = "send email")
    parser.add_argument("message", help = "email's content")
    parser.add_argument("-t","--to", help = "recipient default:bily.lee@qq.com", default = "bily.lee@qq.com")
    parser.add_argument("-su", "--subject", help = "email's subject")
    parser.add_argument("-a", "--attach", help = "the path of the email's attachment")
    parser.add_argument("-sm", "--server", help = "smtp server, e.g. smtp.gmail.com", default = None)
    parser.add_argument("-se", "--sender", help = "default:mclab_speech@163.com", default = "mclab_speech@qq.com")
    parser.add_argument("-p", "--password-from-file", default = "/etc/mail.password")
    args = parser.parse_args()

    SMTP_SERVER = args.server or parse_email_address(args.sender)
    
    SMTP_PORT = 587

    sender = args.sender
    sys.stderr.write("the sender is: " + sender + "\n")

    import base64 # the password is base64 encoded
    password = base64.b64decode(open(args.password_from_file).read())

    recipient = args.to
    sys.stderr.write("the recipient is: " + recipient + "\n")

    subject = args.subject
    attachment = args.attach

    message = args.message

    msg = MIMEMultipart()
    msg['Subject'] = subject 
    msg['To'] = recipient
    msg['From'] = sender
    
    body = MIMEText('text', "plain")
    body.set_payload(message)

    msg.attach(body)
    
    if attachment:
        sys.stderr.write("Adding attachment..." + "\n")
        msgq = parse_attachment(attachment)
        msg.attach(msgq)
    
    # Now send or store the message
    qwertyuiop = msg.as_string()
    
    sys.stderr.write("Connecting to server..." + "\n")
    
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
 
    session.ehlo()
    session.starttls()
    session.ehlo
    
    session.login(sender, password)
 
    session.sendmail(sender, recipient, qwertyuiop)
 
    session.quit()
    os.system('notify-send "Email sent"')
 
if __name__ == '__main__':
    main()
