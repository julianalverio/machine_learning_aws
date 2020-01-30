"""Script for testing emails that you plan to later send out to the entire
class (in our case, this was login info for their AWS machines."""

# Native Python imports
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# External package imports
import smtplib

def test_mail_to_list(MSG_TYPE="restart"):

    # Message information
    name_of_user = "TEST USER"
    ip_address = "0.00.000.00"
    fromaddr = "machinelearning.uruguay@gmail.com"
    toaddr = "TEST_EMAIL @ DOMAIN"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Updated AWS Login Information"

    # Text body of message
    if MSG_TYPE == "full":
        body = """\n
               
               Hola %s,


               Below is your login information for today.
               Today's password: pantalones

               Windows users: please be sure to restart your computer every day before class.
               Mac users and users running Linux: Please
               copy and paste the following commands into
               your command line.
               Windows users: paste the following commands
               into Git Bash, and please remember to RESTART or SHUT DOWN 
               your computer before coming to class.

               1. Set up ssh port forwarding:
               ssh -o "StrictHostKeyChecking no" -NfL 5005:localhost:8888 ubuntu@%s
               Then type the password.

               If you get an error that says something like:
               bind [127.0.0.1]:5005: Address already in use

               Mac and Linux users, run this:
               pkill -f 5005
               Then retry step 1
               
               2. Go to your web browser (such
               as Chrome) and type:
               localhost:5005
               
               This will take you to your AWS Jupyter
               notebooks! If this worked for you, you're all set!


               Mucho amor,
               GSL Uruguay Technical Team
               """ % (name_of_user, ip_address)

    # Prepare email to server information
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(fromaddr, "support_vector_machine")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def main():
    test_mail_to_list()


if __name__ == "__main__":
    main()