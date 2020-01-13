# Native Python imports
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# External package imports
import smtplib

def test_mail_to_list(MSG_TYPE="restart"):
    """Class method for writing to a set of emails determined by email
    information from users.csv.

    The information sent in this email provides information for users on
    how to setup and get into their assigned AWS instances.

    Returns:
        1. A mapping from users to IP addresses that can be used for
            later reference.
    """


    # Message information
    name_of_user = "Ryan Sander"
    ip_address = "0.00.000.00"
    fromaddr = "machinelearning.uruguay@gmail.com"
    toaddr = "rmsander1026@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Updated AWS Login Information"

    # Text body of message
    if MSG_TYPE == "full":
        body = """\

        Hola %s,

        Below is your login information for this course.  
        Mac users and users running Linux: Please
        copy and paste the following command into your command line.
        Windows users: paste the following command into Git Bash


        Next, copy and paste this command:
        ssh -o "StrictHostKeyChecking no" ubuntu@%s

        Next, copy and paste these commands one at a time.

        source ~/.bashrc


        Make sure you paste this command below in ONE line:
        sudo /home/ubuntu/conda/bin/conda env create -f 
        /home/ubuntu/machine_learning_aws/environment.yml -n conda_env

        conda init bash

        conda activate conda_env

        jupyter notebook --port=8888 --no-browser --ip='*' 
        --NotebookApp.token='' --NotebookApp.password='' 
        /home/ubuntu/machine_learning_aws/daily_user


        Paste this command:
        ssh -NfL 5005:localhost:8888 ubuntu@%s


        Finally, your web browser and type:
        localhost:5005


        This will take you to the Jupyter notebooks on AWS that we will 
        be using for the rest of this course!  

        Mucho amor,
        GSL Uruguay Technical Team
        """ % (name_of_user, ip_address, ip_address)

    elif MSG_TYPE == "restart":
        body = """\

        Hola %s,

        Below is your login information for this 
        course.  

        Mac users and users running Linux: Please
        copy and paste the following commands into 
        your command line.

        Windows users: paste the following commands
        into Git Bash

        PASSWORD: pantalones

        1. Connect to your machine:
        ssh -o "StrictHostKeyChecking no" ubuntu@%s


        2. Next, we want to initialize our conda environment:
        conda activate conda_env


        3. Now, we want to install tmux in case we lose connection:
        sudo apt-get install tmux


        4. Now we want to start a tmux session:
        tmux


        5. Next, open a Jupyter notebook:
        jupyter notebook --port=8888 --no-browser --ip='*' --NotebookApp.token='' --NotebookApp.password='' /home/ubuntu/machine_learning_aws/daily_user


        6. Next, detach from your tmux session:
            PRESS (1) ctrl + b (same time), 
             then (2) d (after) on your keyboard


        7. (ON YOUR LOCAL MACHINE) Use ssh port forwarding:
        ssh -NfL 5005:localhost:8888 ubuntu@%s

        8. Finally, go to your web browser (such as Chrome) and type:
        localhost:5005


        This will take you to your AWS Jupyter notebooks!

        Mucho amor,
        GSL Uruguay Technical Team
        """ % (name_of_user, ip_address, ip_address)

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