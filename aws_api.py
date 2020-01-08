import boto3
from pprint import pprint
import time
import os
import csv
import re
import math
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import copy

# reference: https://stackabuse.com/automating-aws-ec2-management-with-python-and-boto3/
'''
Assumptions about this directory:
1. There is a file named ec2-keypair.pem
2. There is folder named template which has all the jupyter notebooks for the class
3. There is a file named email_credentials.txt which has the password for the bot gmail address
4. There is a file users.csv where the first column is full names and the second is email addresses for students
5. You are a collabotor on the machine_learning_aws repo and don't need to manually provide any credentials to push  
'''


class AWSHandler():
    def __init__(self):
        # uid, username, name of user, emaail
        self.user_info = self.get_user_info()
        print(self.user_info)

    # Given that you have properly set up the AWS CLI, this will generate the .pem file to call the methods below
    def generate_keypair(self):
        ec2 = boto3.resource('ec2')
        # outfile = open('ec2-keypair.pem', 'w')
        key_pair = ec2.create_key_pair(KeyName='ec2-keypair')
        KeyPairOut = str(key_pair.key_material)
        print(KeyPairOut)
        with open('ec2-keypair.pem', 'w+') as f:
            f.write(KeyPairOut)

    # Create n instances, wait for them to be 'running', and write down the ip addresses in hosts.txt
    def start_instances(self, count=None, instance_type='t3a.xlarge'):
        if not count:
            count = len(self.user_info)
        #ami = 'ami-00068cd7555f543d5'  # linux
        ami = 'ami-00a208c7cdba991ea'  # ubuntu
        ec2 = boto3.resource('ec2', region_name="us-east-1")
        print("AMI is: {}, instance type is: {}".format(ami, instance_type))
        instances = ec2.create_instances(
            ImageId=ami,
            MinCount=count,
            MaxCount=count,
            InstanceType=instance_type,
            KeyName='ec2-keypair'
        )
        print("AMI is {}".format(ami))
        self.wait_for_instances(['running', 'terminated', 'shutting-down'])

    # returns a list of [instance_id, instance_type, ip_address, current_state] lists.
    def get_instance_info(self):
        client = boto3.client('ec2', region_name="us-east-1")
        data = client.describe_instances()
        # one reservation is one time that you requested machines.
        instance_info = list()
        for reservation in data['Reservations']:
            # number of instances in reservation['Instances'] is the number of machines you requested with that API call
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

    # wait for all the instances to be in a desired set of states. Retry every 10 seconds.
    def wait_for_instances(self, target_states=['running']):
        for target_state in target_states:
            assert target_state in ['pending', 'running', 'stopping', 'stopped', 'shutting-down', 'terminated']
        instances = self.get_instances()
        states = [instance.state['Name'] for instance in instances]
        ready = all([state in target_states for state in states])
        while not ready:
            print('Waiting for instances to reach %s states. Current states: %s' % (target_states, sorted(states)))
            time.sleep(10)
            instances = self.get_instances()
            states = [instance.state['Name'] for instance in instances]
            ready = all([state in target_states for state in states])
        print('Instances are ready!')

    # Terminate all the instanes
    def terminate_instances(self):
        instances = self.get_instances()
        for instance in instances:
            try:
                instance.terminate()
            except:
                pass
        self.wait_for_instances(['terminated'])


    # Read from users.csv. Generate usernames by removing alphanumeric characters from their email username
    # Return list of (username, user's full name, email address) tuples
    def get_user_info(self):
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


    # You only run this once at the beginning of the course
    # Generate a directory with code notebooks for each user.
    def initialize_directories(self):
        usernames = [username for username, _, _ in self.get_user_info()]
        for username in usernames:
            cmd = 'cp -r template users/%s' % username
            os.system(cmd)


    # Once you have run start_instances() and the machines are running, partition the students equally among the machines.
    def assign_students_to_machines(self):
        user_info = self.get_user_info()  # username, user, email
        num_students = len(user_info)
        num_machines = len([state for _, _, _, state in self.get_instance_info() if state == 'running'])
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

    # once you've run start_instances(), ssh into the machines to set up clone the repo, set up conda environments, etc.
    # [instance_id, instance_type, ip_address, current_state] --> instance info
    #     # uid, username, name of user, email --> user info
    def prepare_machine_environments(self, password):
        here = os.getcwd()
        credential_path = os.path.join(here, 'ec2-keypair.pem')
        # for _, _, host, _ in self.get_instance_info():
        #     setup_command = 'sudo python3 /home/ubuntu/machine_learning_aws/setup0.py --pwd %s' % password
        #     clone_command = '"git clone https://github.com/julianalverio/machine_learning_aws.git && %s"' % setup_command
        #     ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no" ubuntu@%s %s' % (credential_path, host, clone_command)
        #     print(ssh_command)
        #     os.system(ssh_command)

        for _, _, host, _ in self.get_instance_info():
            setup_command = 'sudo python3 machine_learning_aws/setup1.py --users placeholder --pwd %s' % (password)
            clone_command = '"sudo rm -rf machine_learning_aws; git clone https://github.com/julianalverio/machine_learning_aws.git && %s"' % setup_command
            ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no" ubuntu@%s %s' % (credential_path, host, clone_command)
            print(ssh_command)
            os.system(ssh_command)

        # counter = 0  # Begin counter at zero
        # for _, _, host, _ in self.get_instance_info():
        #     setup_command = 'sudo python3 /home/ubuntu/machine_learning_aws/setup2.py --users placeholder ' \
        #                     '--port_counters %s' % counter
        #     ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no" ubuntu@%s %s' % (credential_path, host, setup_command)
        #     print(ssh_command)
        #     os.system(ssh_command)
        #     counter += 1  # Increment counter for remote porting
        print('Done! This print statement does not guarantee success.')

    # uid, username, name of user, email --> user info
    # [instance_id, instance_type, ip_address, current_state] --> instance info
    def mail_to_list(self):
        instance_info = self.get_instance_info()
        assert len([state for _, _, _, state in instance_info if state == 'running']) == len(self.user_info), 'number of machines does not match number of students'

        for (uid, username, name_of_user, email),  (_, _, ip_address, _) in zip(self.user_info, instance_info):
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
            scp_command = 'scp -i %s -o "StrictHostKeyChecking no" ubuntu@%s:/home/ubuntu/machine_learning_aws/  %s' % (credential_path, host, host_save_dir)
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
            scp_command = 'scp -i %s -o "StrictHostKeyChecking no" %s ubuntu@%s:/home/ubuntu/machine_learning_aws/  %s' % (credential_path, local_source, host, remote_destination)
            os.system(scp_command)

    def push_button(self):
        self.start_instances()
        self.prepare_machine_environments()
        # self.mail_to_list()


# def main_debugging():
#     API = AWS_API()
#     print(API.get_user_info())
#
#     API.terminate_instances()
#     API.start_instances(count=1, instance_type='t3a.xlarge')
#     time.sleep(10)  # TODO: Might not need this
#     API.get_instance_info()
#     #API.prepare_machine_environments('test')

def main():
    """Main script for running startup of AWS instances."""
    API = AWSHandler()  # Instantiate class object
    # API.terminate_instances()

    API.start_instances(count=2, instance_type='m5a.large')
    time.sleep(30)
    API.prepare_machine_environments('test')



if __name__=="__main__":
    main()

