import os
import csv
import yagmail
import smtplib


# csv should have full name in the first column, emails in the second column
def authenticate_email():
    with open('email_credentials.txt', 'r') as f:
        password = f.read().strip()
    print(password)
    username = 'machinelearning.uruguay@gmail.com'
    yag = yagmail.SMTP(username, password)
    return yag


# yag = authenticate_email()
# yag = yagmail.SMTP('machinelearning.uruguay@gmail.com', 'support_vector_machine')
# content = 'this is a test'
# yag.send('The first email test', 'This is the body')

import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
except:
    print('Something went wrong...')
