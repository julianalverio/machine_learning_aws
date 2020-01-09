"""AWS API script for setting up all of our EC2 machines.  Our class object
AWSHandler() also makes calls to other relevant scripts in this repository. """

import boto3
import time
import os
import csv
import re
import math
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
        # outfile = open('ec2-keypair.pem', 'w')
        key_pair = ec2.create_key_pair(KeyName='ec2-keypair2')
        KeyPairOut = str(key_pair.key_material)
        print(KeyPairOut)
        with open('ec2-keypair.pem', 'w+') as f:
            f.write(KeyPairOut)

        print("Keypair written")

    def start_instances(self, count=None, instance_type='t3a.xlarge',
                        ami_type="ubuntu"):
        """Function for starting new EC2 instances from scratch.  This
        function creates n instances, waits for them to be 'running',
        and writes down the ip addresses in hosts.txt.
        """

        if not count:
            count = len(self.user_info)

        # Choose AMI - by default this is Ubuntu
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
                instance_IDs.write(ID+"\n")

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


    def restart_instances(self, count=None, instance_type='t3a.xlarge'):
        if not count:
            count = len(self.user_info)
        ec2 = boto3.resource('ec2', region_name="us-east-1")
        print("AMI is: {}, instance type is: {}".format(ami, instance_type))
        instances = self.get_instances()
        # Now iterate through instances
        instance_ids = []
        for instance in instances:
            instance_ids.append(instance.instance_id)
        # Now restart all instances at once
        try:
            ec2.reboot_instances(InstanceIds=instance_ids, DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                print("You don't have permission to reboot instances.")
                raise


        print("AMI is {}".format(ami))
        self.wait_for_instances(['running', 'terminated', 'shutting-down'])

    # returns a list of [instance_id, instance_type, ip_address, current_state] lists.
    def get_instance_info(self):
        """Function for retrieving instance-related information.

        Returns a
        list of [
        instance_id,
        instance_type,
        ip_address,
    # current_state] lists."""
        client = boto3.client('ec2', region_name="us-east-1")
        data = client.describe_instances()
        # one reservation is one time that you requested machines.
        instance_info = list()
        for reservation in data['Reservations']:
            # number of instances in reservation['Instances'] is the number
            # of machines you requested with that API call
            for instance_dict in reservation['Instances']:
                uid = instance_dict['InstanceId']
                instance_type = instance_dict['InstanceType']
                state = instance_dict['State']['Name']
                if 'PublicIpAddress' in instance_dict:
                    ip_address = instance_dict['PublicIpAddress']
                else:
                    ip_address = None
                if state != 'running':
                    continue
                instance_info.append([uid, instance_type, ip_address, state])
        return instance_info

    # return all instance objects
    def get_instances(self):
        ec2 = boto3.resource('ec2')
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

    # Terminate all the instances
    def terminate_instances(self):
        instances = self.get_instances()
        for instance in instances:
            try:
                instance.terminate()
            except:
                print("Unable to terminate instance %s" % instance)
        self.wait_for_instances(['terminated'])
    
    # Stop all the instances
    def hibernate_instances(self):
        """Function for stopping all active instances at the end of a work
        session"""
        instances = self.get_instances()
        for instance in instances:
            try:
                instance.terminate()
            except:
                print("Unable to hibernate instance %s" % instance)
        self.wait_for_instances(['stopping', 'stopped', 'terminated'])


    # Stop all the instances
    def hibernate_instances(self):
        """Function for stopping all active instances at the end of a work
        session"""
        instances = self.get_instances()
        for instance in instances:
            try:
                instance.terminate()
            except:
                print("Unable to hibernate instance %s" % instance)
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
        return user_info

    # You only run this once at the beginning of the course
    # Generate a directory with code notebooks for each user.
    def initialize_directories(self):
        usernames = [username for username, _, _ in self.get_user_info()]
        for username in usernames:
            cmd = 'cp -r template users/%s' % username
            os.system(cmd)

    # Once you have run start_instances() and the machines are running,
    # partition the students equally among the machines.
    def assign_students_to_machines(self):
        user_info = self.get_user_info()  # username, user, email
        num_students = len(user_info)
        num_machines = len(
            [state for _, _, _, state in self.get_instance_info() if
             state == 'running'])
        students_per_machine = math.ceil(num_students / num_machines)
        groups = list()
        group = ''
        counter = 0
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

    # # helper function for threading in prepare_machine_environments()
    # def run_setup_command(self, command):
    #     print(command)
    #     os.system(command)

    # once you've run start_instances(), ssh into the machines to set up
    # clone the repo, set up conda environments, etc.
    # [instance_id, instance_type, ip_address, current_state] --> instance info
    #     # uid, username, name of user, email --> user info
    def prepare_machine_environments(self, password):
        here = os.getcwd()
        credential_path = os.path.join(here, 'ec2-keypair.pem')
        # for _, _, host, _ in self.get_instance_info():
        #     setup_command = 'sudo python3
        #     /home/ubuntu/machine_learning_aws/setup0.py --pwd %s' % password
        #     clone_command = '"git clone
        #     https://github.com/julianalverio/machine_learning_aws.git &&
        #     %s"' % setup_command
        #     ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no"
        #     ubuntu@%s %s' % (credential_path, host, clone_command)
        #     print(ssh_command)
        #     os.system(ssh_command)

        for _, _, host, _ in self.get_instance_info():
            setup_command = 'sudo python3 machine_learning_aws/setup1.py ' \
                            '--users placeholder --pwd %s' % (
                password)
            clone_command = '"sudo rm -rf machine_learning_aws; git clone ' \
                            'https://github.com/julianalverio/machine_learning_aws.git && %s"' % setup_command
            ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no" ubuntu@%s ' \
                          '%s' % (
            credential_path, host, clone_command)
            print(ssh_command)
            os.system(ssh_command)

        # counter = 0  # Begin counter at zero
        # for _, _, host, _ in self.get_instance_info():
        #     setup_command = 'sudo python3
        #     /home/ubuntu/machine_learning_aws/setup2.py --users placeholder
        #     ' \
        #                     '--port_counters %s' % counter
        #     ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no"
        #     ubuntu@%s %s' % (credential_path, host, setup_command)
        #     print(ssh_command)
        #     os.system(ssh_command)
        #     counter += 1  # Increment counter for remote porting
        print('Done! This print statement does not guarantee success.')

    # uid, username, name of user, email --> user info
    # [instance_id, instance_type, ip_address, current_state] --> instance info
    def mail_to_list(self):
        instance_info = self.get_instance_info()

        broken_emails = list()
        ip_address_to_useremail_user = dict()
        num_users = len(self.user_info)
        for idx, ((uid, username, name_of_user, email),
                  (_, _, ip_address, _)) in enumerate(
                zip(self.user_info, instance_info)):
            ip_address_to_useremail_user[ip_address] = [email, username]
            print('Sending email %s out of %s' % ((idx + 1), num_users))
            fromaddr = "machinelearning.uruguay@gmail.com"
            toaddr = email
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Daily Log In Instructions"
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

            body = 'We are testing some things, please ignore this :) '

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
        print(broken_emails)
        return ip_address_to_useremail_user

    def get_available_ip_addresses(self):
        instance_info = self.get_instance_info()
        ip_addresses = [ip_address for _, _, ip_address, _ in instance_info]
        ip_address_to_useremail_user = dict()
        for idx, ((uid, username, name_of_user, email),
                  (_, _, ip_address, _)) in enumerate(
                zip(self.user_info, instance_info)):
            ip_address_to_useremail_user[ip_address] = [email, username]
        remaining_ip_addresses = list()
        for address in ip_addresses:
            if address not in ip_address_to_useremail_user:
                remaining_ip_addresses.append(address)
        print('remaining ip addresses:', remaining_ip_addresses)
        return remaining_ip_addresses

    # this needs to be tested
    def backup_machines(self):
        # get ip addresses for all live machines
        live_addresses = list()
        for _, _, ip_address, state in self.get_instance_info():
            if state == 'running':
                live_addresses.append(ip_address)

        # make a directory where you can clone all the local copies of the repo
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
        for host in live_addresses:
            host_save_dir = os.path.join(root_save_dir, host)
            scp_command = 'scp -i %s -o "StrictHostKeyChecking no" ' \
                          'ubuntu@%s:/home/ubuntu/machine_learning_aws/  %s' % (
            credential_path, host, host_save_dir)
            os.system(scp_command)
            os.chdir(host_save_dir)
            os.system('git add .')
            os.system('git commit -m "push for %s"' % host)
            os.system('git push')

    # this needs to be tested
    # TODO: can we wget this from dropbox or Google Drive or something?
    def transfer_data(self):
        remote_destination = '/home/ubuntu/'  # TODO: edit this
        local_source = os.path.join(os.getcwd(), 'something')  # TODO: edit this
        credential_path = os.path.join(os.getcwd(), 'ec2-keypair.pem')
        live_addresses = list()
        for _, _, ip_address, state in self.get_instance_info():
            if state == 'running':
                live_addresses.append(ip_address)
        for host in live_addresses:
            scp_command = 'scp -i %s -o "StrictHostKeyChecking no" %s ' \
                          'ubuntu@%s:/home/ubuntu/machine_learning_aws/  %s' % (
            credential_path, local_source, host, remote_destination)
            scp_command = 'scp -i %s -o "StrictHostKeyChecking no" %s ubuntu@%s:/home/ubuntu/machine_learning_aws/  %s' % (credential_path, local_source, host, remote_destination)


    def full_start(self, email=True):
        self.terminate_instances()
        self.start_instances(count=65, instance_type='t3a.xlarge')
        time.sleep(120)
        self.prepare_machine_environments('pantalones')



def main():
    """Main script for running AWS API commands."""
    EMAIL = False
    FULL_START = False
    ROLLING_START = False
    SAVE_INSTANCE_IDs = True

    # Instantiate class instance
    API = AWSHandler()

    # Based off of boolean flags, run specific commands for AWS
    if FULL_START:
        API.start_instances(count=65, instance_type='t3a.xlarge')
    elif ROLLING_START:
        API.start_instances()

    # Choose whether we email to class
    if EMAIL:
        API.mail_to_list()

    # Choose whether or not to save active instance IDs
    if SAVE_INSTANCE_IDs:
        API.save_instance_ids()


if __name__ == "__main__":
    main()
