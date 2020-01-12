"""AWS API script for setting up all of our EC2 machines.  Our class object
AWSHandler() also makes calls to other relevant scripts in this repository. """

# Native Python imports
import time
import os
import csv
import re
import math
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# External package imports
import boto3
import smtplib

"""
Reference for this project: 
https://stackabuse.com/automating-aws-ec2-management-with-python-and-boto3/

Assumptions about the current working directory:
1. There is a file named ec2-keypair.pem.
2. There is folder named template which has all the jupyter notebooks for the 
    class/.
3. There is a file named email_credentials.txt which has the password for the 
    bot gmail address.
4. There is a file users.csv where the first column is full names and the 
    second is email addresses for students.
5. You are a collaborator on the machine_learning_aws repo and don't need to 
    manually provide any credentials to push.
"""


class AWSHandler():
    """Main object for starting and stopping instances, creating new
    instances, retrieving instance and user information, and sending emails
    to users for information on their assigned AWS instances.
    """

    def __init__(self):
        self.user_info = self.get_user_info()

    def generate_keypair(self):
        """Given that you have properly set up the AWS CLI, this will generate
        the .pem file to call the methods below.  This cannot be done if
        someone else has already """
        ec2 = boto3.resource('ec2')
        key_pair = ec2.create_key_pair(KeyName='ec2-keypair2')
        KeyPairOut = str(key_pair.key_material)
        print(KeyPairOut)
        with open('ec2-keypair.pem', 'w+') as f:
            f.write(KeyPairOut)

        print("Keypair written")

    def start_instances(self, count=None, instance_type='t3a.xlarge',
                        ami_type="ubuntu", custom_ami_name=None):
        """Function for starting new EC2 instances from scratch.  This
        function creates n instances, waits for them to be 'running',
        and writes down the ip addresses in hosts.txt.
        """

        if not count:
            count = len(self.user_info)
        print("Count is {}".format(count))

        # Choose AMI - by default this is Ubuntu
        if custom_ami_name is not None:  # If we want to use a custom AMI
            ami = custom_ami_name
        else:  # Use a specific AMI
            if ami_type == "ubuntu":
                ami = 'ami-00a208c7cdba991ea'  # ubuntu
            elif ami_type == "linux":
                ami = 'ami-00068cd7555f543d5'  # linux

        # Create EC2 object
        ec2 = boto3.resource('ec2', region_name="us-east-1")
        print("AMI is: %s, instance type is: %s" % (ami, instance_type))

        # Now create instances using AMI
        instances = ec2.create_instances(
            ImageId=ami,
            MinCount=count,
            MaxCount=count,
            InstanceType=instance_type,
            KeyName='ec2-keypair'
        )

        # After creating instances, hang
        self.wait_for_instances(['running', 'terminated', 'shutting-down'])

    def save_instance_ids(self):
        """Class method for saving our active instance IDs to a text file for
        later use in re-activating the instances after they have been stopped
        (not terminated).  These IDs are saved to instance_IDs.txt.
        """

        # Get all our active instances
        instances = self.get_instances()

        # Create an instance ID text file to use for later
        with open("instance_IDs.txt", "w") as instance_IDs:
            # Iterate through all instances
            for instance in instances:
                # Get specific instance ID
                ID = instance.instance_id

                # Write instance ID to file
                instance_IDs.write(ID + "\n")

            # Close file writer object when finished
            instance_IDs.close()
        print("Instance IDs saved to instance_ids.txt in cwd")

    def restart_instances(self):
        """Function for restarting instances that have been stopped, but not
        terminated.  This function is typically used if we want to restart
        instances that have had Anaconda environments already installed on
        them (i.e. maintain an offline, persistent state).
        """

        ec2 = boto3.resource('ec2', region_name="us-east-1")
        print("AMI is: {}, instance type is: {}".format(ami, instance_type))
        instances = self.get_instances()

        # Now iterate through instances and append ID to list of IDs
        with open("instance_IDs.txt", "r") as instance_IDs:
            instance_IDs.read()
            instance_IDs.close()

        # Now restart all instances at once
        try:  # Try to restart the instance
            instances = ec2.reboot_instances(InstanceIds=instance_ids,
                                             DryRun=True)

        except ClientError as e:  # In case we cannot restart instances
            if 'DryRunOperation' not in str(e):
                print("You don't have permission to reboot instances.")
                raise

        print("Stopped instances have been restarted \n Instance names:")
        # Print all the instance names
        for instance in instances:
            print(instance.instance_id)

        # After creating instances, hang
        self.wait_for_instances(['running', 'terminated', 'shutting-down'])

    def get_instance_info(self):
        """Function for retrieving instance-related information using
        instances that are currently active and associated with the .pem key
        file in this directory.

        Returns:
            A list of [instance_id, instance_type, ip_address, current_state]
            lists indexed by each instance.
        """

        # Make EC2 client
        client = boto3.client('ec2', region_name="us-east-1")
        data = client.describe_instances()

        # One reservation is one time that you requested machines.
        instance_info = list()
        for reservation in data['Reservations']:

            # number of instances in reservation['Instances'] is the number
            # of machines you requested with that API call
            for instance_dict in reservation['Instances']:

                # Get instance-related information
                uid = instance_dict['InstanceId']
                instance_type = instance_dict['InstanceType']
                state = instance_dict['State']['Name']

                if 'PublicIpAddress' in instance_dict:
                    ip_address = instance_dict['PublicIpAddress']
                else:
                    ip_address = None
                if state != 'running':
                    continue

                # Add all info about specific instance
                instance_info.append([uid, instance_type, ip_address, state])

        return instance_info

    def get_instances(self):
        """Class method for retrieving all instance objects.

        Returns:
            A list of EC2 instance class objects.
        """

        # Create EC2 resource
        ec2 = boto3.resource('ec2')

        # Iterate through instances
        instances = list()
        for instance_id, _, _, _ in self.get_instance_info():
            instances.append(ec2.Instance(instance_id))

        return instances

    # wait for all the instances to be in a desired set of states. Retry
    # every 10 seconds.
    def wait_for_instances(self, target_states=['running']):
        for target_state in target_states:
            assert target_state in ['pending', 'running', 'stopping', 'stopped',
                                    'shutting-down', 'terminated']
        instances = self.get_instances()
        states = [instance.state['Name'] for instance in instances]
        ready = all([state in target_states for state in states])
        while not ready:
            print(
                'Waiting for instances to reach %s states. Current states: '
                '%s' % (
                    target_states, sorted(states)))
            time.sleep(10)
            instances = self.get_instances()
            states = [instance.state['Name'] for instance in instances]
            ready = all([state in target_states for state in states])
        print('Instances are ready!')

    def terminate_instances(self):
        """Class method for terminating all active EC2 instances.
        """

        # Get instances and iteratively terminate them
        instances = self.get_instances()
        for instance in instances:
            try:
                instance.terminate()
            except:
                print("Unable to terminate instance %s" % instance)

        # After creating instances, hang
        self.wait_for_instances(['terminated'])

    def hibernate_instances(self):
        """Class method for stopping all active instances at the end of a work
        session.  Keeps all of the prior installations on each machine
        active.

        NOTE: Running this class method will ensure that the owner of these
        instances will not incur EC2 usage charges, but it will incur EBS
        storage costs.
        """

        # Get instances and iteratively stop them
        instances = self.get_instances()
        for instance in instances:
            try:
                instance.stop()
            except:
                print("Unable to hibernate instance %s" % instance)

        # After creating instances, hang
        self.wait_for_instances(['stopping', 'stopped', 'terminated'])

    def get_user_info(self):
        """Read from users.csv. Generate usernames by removing alphanumeric
        characters from their email username.

        Returns:
             list of (username, user's full name, email address) tuples."""

        # Opens users file and reads row
        with open('users.csv', 'rU') as f:
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

            # Close the file
            f.close()

        return user_info

    def initialize_directories(self):
        """Note: You only run this once at the beginning of the course.
        This class method generates a directory with code notebooks for each
        user.
        """

        # Get user names from class method
        usernames = [username for username, _, _ in self.get_user_info()]
        for username in usernames:
            cmd = 'cp -r template users/%s' % username
            os.system(cmd)

    def assign_students_to_machines(self):
        """Class method for pairing students with machines.  Once you have run
        start_instances() and the machines are running,
        partition the students equally among the machines.

        Returns:
            1. A list of groups containing information about the pairings
            between users and IP addresses for the EC2 computers.
        """

        # Get user info and number of students
        user_info = self.get_user_info()  # username, user, email
        num_students = len(user_info)
        num_machines = len(
            [state for _, _, _, state in self.get_instance_info() if
             state == 'running'])

        # Compute students per machine
        students_per_machine = math.ceil(num_students / num_machines)
        groups = list()
        group = ''
        counter = 0

        # Iterate through user information and emails
        for username, _, email in user_info:
            if counter < students_per_machine:
                group += username + ','
            else:
                groups.append(group[:-1])
                group = ''
                counter = 0
            counter += 1
        groups.append(group[:-1])
        return groups

    def prepare_machine_environments(self, password, custom_ami="no"):
        """Function for setting up our active instances.  Once you've run
        start_instances():

            1. ssh into the machines
            2. clone the repo
            3. set up conda environments, etc.

        Note the following: [instance_id, instance_type, ip_address,
        current_state] --> instance info
        uid, username, name of user, email --> user info
        """

        # Get credentials
        here = os.getcwd()
        credential_path = os.path.join(here, 'ec2-keypair.pem')

        # Iterate through hosts and create commands for configuring computers
        print("INSTANCE INFO: {}".format(self.get_instance_info()))

        # Iterate through hosts for setup
        index = 0
        for _, _, host, _ in self.get_instance_info():

            # For progress display only
            print("Iterated through {} hosts".format(index))
            print("Custom AMI: {}".format(custom_ami))

            # Commands used for ssh login
            setup_command = 'sudo python3 machine_learning_aws/setup.py ' \
                            '--pwd %s --custom_ami %s' % (password, custom_ami)
            print(setup_command)
            clone_command = '"sudo rm -rf machine_learning_aws; git clone ' \
                            'https://github.com/julianalverio/machine_learning_aws.git && %s"' % setup_command

            # Only need to do setup, not clone
            if custom_ami == "yes":
                ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no" ' \
                              'ubuntu@%s %s' % (credential_path, host, clone_command)

            # If creating from scratch, run setup + clone repository
            else:
                ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no" ' \
                              'ubuntu@%s %s' % (credential_path, host, clone_command)

            # ssh login and run relevant command
            os.system(ssh_command)

            # Increment counter and repeat
            index += 1

    def mail_to_list(self, MSG_TYPE="both"):
        """Class method for writing to a set of emails determined by email
        information from users.csv.

        The information sent in this email provides information for users on
        how to setup and get into their assigned AWS instances.

        Returns:
            1. A mapping from users to IP addresses that can be used for
                later reference.
        """

        # Get active instance information
        instance_info = self.get_instance_info()

        # Prepare to send emails
        broken_emails = list()
        ip_address_to_useremail_user = dict()
        num_users = len(self.user_info)

        # Iterate through ids and send an email for each user
        for idx, ((uid, username, name_of_user, email),
                  (_, _, ip_address, _)) in enumerate(
            zip(self.user_info, instance_info)):
            # Create mapping from IP address to users
            ip_address_to_useremail_user[ip_address] = [email, username]
            print('Sending email %s out of %s' % ((idx + 1), num_users))

            # Message information
            fromaddr = "machinelearning.uruguay@gmail.com"
            toaddr = email
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "FIXED Updated AWS Login Information"

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
                    sudo /home/ubuntu/conda/bin/conda env create -f /home/ubuntu/machine_learning_aws/environment.yml -n conda_env

                    conda init bash

                    conda activate conda_env

                    jupyter notebook --port=8888 --no-browser --ip='*' --NotebookApp.token='' --NotebookApp.password='' /home/ubuntu/machine_learning_aws/daily_user


                    Paste this command:
                    ssh -NfL 5005:localhost:8888 ubuntu@%s


                    Finally, your web browser and type:
                    localhost:5005


                    This will take you to the Jupyter notebooks on AWS that 
                    we will 
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
                    
                    2. Now, we want to install tmux in case we lose connection:
                    sudo apt-get install tmux


                    3. Now we want to start a tmux session:
                    tmux


                    4. Next, we want to initialize our conda environment:
                    conda activate conda_env


                    5. Next, open a Jupyter notebook:
                    jupyter notebook --port=8888 --no-browser --ip='*' --NotebookApp.token='' --NotebookApp.password='' /home/ubuntu/machine_learning_aws/daily_user


                    6. Next, detach from your tmux session:
                    PRESS (1) ctrl + b (same time), 
                     then (2) d (after) on your keyboard


                    7. (ON YOUR LOCAL MACHINE IN A NEW TERMINAL) Use ssh port forwarding:
                    ssh -NfL 5005:localhost:8888 ubuntu@%s


                    8. Finally, go to your web browser (such as Chrome) and type:
                    localhost:5005


                    This will take you to your AWS Jupyter notebooks!

                    Mucho amor,
                    GSL Uruguay Technical Team
                    """ % (name_of_user, ip_address, ip_address)

            elif MSG_TYPE == "both":
                body = """\
                    Hola User,

                    Below is your login information for this 
                    course.  

                    Mac users and users running Linux: Please
                    copy and paste the following commands into 
                    your command line.

                    Windows users: paste the following commands
                    into Git Bash

                    PASSWORD: pantalones
                    
                    IF YOU DID NOT RECEIVE AN EMAIL FROM US EARLIER, DO THIS:
                    
                    1. Connect to your machine:
                    ssh -o "StrictHostKeyChecking no" ubuntu@%s
                    
                    
                    2. Now, we want to install tmux in case we lose connection:
                    sudo apt-get install tmux


                    3. Now we want to start a tmux session:
                    tmux
                    
                    
                    4. Now we source our bash:
                    source ~/.bashrc​
                    
                    
                    5. Now we want to re-install our Anaconda environment:
                    sudo /home/ubuntu/conda/bin/conda env create -f /home/ubuntu/machine_learning_aws/environment.yml -n conda_env


                    6. Next, we want to initialize our conda environment:
                    conda activate conda_env


                    7. Next, open a Jupyter notebook:
                    jupyter notebook --port=8888 --no-browser --ip='*' --NotebookApp.token='' --NotebookApp.password='' /home/ubuntu/machine_learning_aws/daily_user


                    8. Next, detach from your tmux session:
                    PRESS (1) ctrl + b (same time), 
                     then (2) d (after) on your keyboard


                    9. (ON YOUR LOCAL MACHINE IN A NEW TERMINAL) Use ssh port forwarding:
                    ssh -NfL 5005:localhost:8888 ubuntu@%s


                    10. Finally, go to your web browser (such as Chrome) and type:
                    localhost:5005
                    
                    IF YOU DID RECEIVE AN EMAIL FROM US EARLIER, DO THIS:
                    1. Connect to your machine:
                    ssh -o "StrictHostKeyChecking no" ubuntu@%s
                    
                    2. Now, we want to install tmux in case we lose connection:
                    sudo apt-get install tmux


                    3. Now we want to start a tmux session:
                    tmux


                    4. Next, we want to initialize our conda environment:
                    conda activate conda_env


                    5. Next, open a Jupyter notebook:
                    jupyter notebook --port=8888 --no-browser --ip='*' --NotebookApp.token='' --NotebookApp.password='' /home/ubuntu/machine_learning_aws/daily_user


                    6. Next, detach from your tmux session:
                    PRESS (1) ctrl + b (same time), 
                     then (2) d (after) on your keyboard


                    7. (ON YOUR LOCAL MACHINE IN A NEW TERMINAL) Use ssh port forwarding:
                    ssh -NfL 5005:localhost:8888 ubuntu@%s


                    8. Finally, go to your web browser (such as Chrome) and type:
                    localhost:5005


                    This will take you to your AWS Jupyter notebooks!

                    Mucho amor,
                    GSL Uruguay Technical Team
                    


                    This will take you to your AWS Jupyter notebooks!

                    Mucho amor,
                    GSL Uruguay Technical Team
                    """ % (ip_address, ip_address, ip_address, ip_address)

            elif MSG_TYPE == "custom_ami":
                body = """\
                   Hola %s,

                   Below is your login information for this 
                   course.  

                   Mac users and users running Linux: Please
                   copy and paste the following commands into 
                   your command line.

                   Windows users: paste the following commands
                   into Git Bash.

                   PASSWORD: pantalones

                   1. Connect to your machine:
                   ssh -o "StrictHostKeyChecking no" ubuntu@%s


                   2. Next, detach from your auto-generated tmux session:
                   PRESS (1) ctrl + b (same time), 
                    then (2) d (after) on your keyboard

                   Note that this automatically starts a Jupyter notebook on port 8889.  You can close this other notebook if you would like, but it is not necessary for you to.

                   
                   3. (ON YOUR LOCAL MACHINE IN A NEW 
                   TERMINAL) Use ssh port forwarding:
                   ssh -NfL 5005:localhost:8888 ubuntu@%s


                   4. Finally, go to your web browser (such 
                   as Chrome) and type:
                   localhost:5005

                   This will take you to your AWS Jupyter 
                   notebooks!

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

        print('This is the information for the broken email addresses')

        # Get broken emails
        print(broken_emails)

        return ip_address_to_useremail_user

    def get_available_ip_addresses(self):
        """Class method for seeing what additional IP addresses are available
        after users are paired to IP addresses.

        Returns:
            1. A list of strings denoting the remaining IP addresses.
        """

        # Get instance information
        instance_info = self.get_instance_info()
        ip_addresses = [ip_address for _, _, ip_address, _ in instance_info]
        ip_address_to_useremail_user = dict()

        # Iterate through users, user names
        for idx, ((uid, username, name_of_user, email),
                  (_, _, ip_address, _)) in enumerate(
            zip(self.user_info, instance_info)):
            # Add (key, value) pair to mapping
            ip_address_to_useremail_user[ip_address] = [email, username]

        # Iterate and find remaining IP addresses
        remaining_ip_addresses = list()
        for address in ip_addresses:
            if address not in ip_address_to_useremail_user:
                remaining_ip_addresses.append(address)

        # Display and return remaining IP addresses
        print('remaining ip addresses:', remaining_ip_addresses)
        return remaining_ip_addresses

    # TODO: Test
    def backup_machines(self):
        """Class method for backing up student-populated content from the
        course to GitHub under the 'daily_users/' sub-directory.
        """

        # Get IP addresses for all live machines and iterate through them
        live_addresses = list()
        for _, _, ip_address, state in self.get_instance_info():
            if state == 'running':
                live_addresses.append(ip_address)

        # Make a directory where you can clone all the local copies of the repo
        here = os.getcwd()
        root_save_dir = os.path.join(here, 'student_copies')
        try:
            os.mkdir(save_dir)
        except FileExistsError:
            pass
        for host in live_addresses:
            host_save_dir = os.path.join(root_save_dir, host)
            try:
                os.mkdir(host_save_dir)
            except FileExistsError:
                pass

        credential_path = os.path.join(here, 'ec2-keypair.pem')

        # Iterate through hosts at different IP addresses
        for host in live_addresses:

            # Make host directory according to IP address
            host_save_dir = os.path.join(root_save_dir, host)

            # File transfer command
            scp_command = 'scp -i %s -o "StrictHostKeyChecking no" ' \
                          'ubuntu@%s:/home/ubuntu/machine_learning_aws' \
                          '/daily_user/  %s' % (
                              credential_path, host, host_save_dir)

            # Transfer files, change directory, then add changes to git repo
            os.system(scp_command)
            os.chdir(host_save_dir)
            os.system('git add .')
            os.system('git commit -m "push for %s"' % host)
            os.system('git push')

    def full_start(self, email=True, num_machines=65):
        """Wrapper function for running start-up of all machines from a
        non-custom AMI.  """

        # Terminate any running instances
        self.terminate_instances()

        # Start new instances
        self.start_instances(count=num_machines, instance_type='t3a.xlarge')

        # Wait until all are fully initialized before preparing envs
        time.sleep(120)

        # Setup and configure instance environments iteratively
        self.prepare_machine_environments('pantalones')

        # Email if designated to
        if email:
            self.mail_to_list()


def main():
    """Main script for running AWS API commands."""

    # Flags for different commands
    EMAIL = False
    EMAIL_CUSTOM = False
    FULL_START = False
    CUSTOM_AMI_START = True
    FULL_CUSTOM_START = False
    ROLLING_START = False
    SAVE_INSTANCE_IDs = False
    HIBERNATE = False
    TERMINATE = False
    DEBUGGING = False
    SETTING_UP_AMI = False

    # Password for configuring machine environments
    PSWD = 'pantalones'

    # Instantiate class instance
    API = AWSHandler()

    # Based off of boolean flags, run specific commands for AWS
    if FULL_CUSTOM_START:
        # TODO: Complete
        API.start_instances(count=65, instance_type='t3a.xlarge')
    elif FULL_START:
        API.start_instances(count=65, instance_type='t3a.xlarge')
        API.prepare_machine_environments(PSWD)
    elif ROLLING_START:
        API.restart_instances()

    # Stop instances/terminate
    if HIBERNATE:
        API.hibernate_instances()
    elif TERMINATE:
        API.terminate_instances()

    # Choose whether we email to class
    if EMAIL:
        API.mail_to_list()
    elif EMAIL_CUSTOM:  # USE THIS IF USING CUSTOM AMIs
        API.mail_to_list(MSG_TYPE="custom_ami")

    # Choose whether or not to save active instance IDs
    if SAVE_INSTANCE_IDs:
        API.save_instance_ids()

    # Debugging
    if DEBUGGING:
        print(API.get_user_info())
        print(API.get_instance_info())

    # Create a single instance for modification
    if SETTING_UP_AMI:
        #API.start_instances(count=1, instance_type='t3a.xlarge')
        #time.sleep(30)
        API.prepare_machine_environments(PSWD, custom_ami="no")

    # Create instances from a custom AMI
    if CUSTOM_AMI_START:
        API.start_instances(count=1, instance_type='t3a.xlarge',
                            custom_ami_name="ami-09f01c0e0942ad784")
        time.sleep(30)
        API.prepare_machine_environments(PSWD, custom_ami="yes")


if __name__ == "__main__":
    main()
