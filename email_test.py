import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_user_info():
    with open('users.csv', 'r') as f:
        reader = csv.reader(f)
        user_info = list()
        for idx, row in enumerate(reader):
            user = row[0]
            email = row[1]
            if not (user and email):
                continue
            username = re.sub('[^0-9a-zA-Z]+', '', email.split(
                '@')[0]).lower()
            user_info.append((idx, username, user, email))
    return user_info

def mail_to_list():
    instance_info = self.get_instance_info()
    assert len([state for _, _, _, state in instance_info if
                state == 'running']) == len(
        self.user_info), 'number of machines does not match number of students'

    for (uid, username, name_of_user, email), (_, _, ip_address, _) in zip(
            self.user_info, instance_info):
        # user_info = self.get_user_info()
        # N = len(user_info)

        # # Get usernames, names, and emails
        # usernames = [user_info[i][0] for i in range(N)]
        # names = [user_info[i][1] for i in range(N)]
        # emails = [user_info[i][2] for i in range(N)]
        # Iterate through usernames, names, and emails
        # port_counter = 0
        # for uname, name, email_addr in zip(usernames, names, emails):
        fromaddr = "machinelearning.uruguay@gmail.com"
        toaddr = email
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Daily Log In Information"
        body = """\

        Hola %s,

        Below is your login information for this course.  
        Mac users and users running Linux: Please
        copy and paste the following command into your command line
        Windoes users: paste the following command into Git Bash

        ssh -NfL 8888:localhost:8888 ubuntu@%s

        Leave this running in your command line/Git Bash console.
        Then open your web browser and type:
        localhost:8888

        This will take you to the Jupyter notebooks on AWS that we will 
        be using for the rest of this course!  

        Mucho amor,
        GSL Uruguay Technical Team
        """ % (name_of_user, ip_address)

        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(fromaddr, "support_vector_machine")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()

        # # Increment port counter by 1 for each user
        # port_counter += 1

def main():
    mail_to_list()

if __name__ == "__main__":
    main()