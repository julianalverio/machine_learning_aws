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
import re

# reference: https://stackabuse.com/automating-aws-ec2-management-with-python-and-boto3/
'''
Assumptions about this directory:
1. There is a file named ec2-keypair.pem
2. There is folder named template which has all the jupyter notebooks for the class
3. There is a file named email_credentials.txt which has the password for the bot gmail address
4. There is a file users.csv where the first column is full names and the second is email addresses for students
5. You are a collabotor on the machine_learning_aws repo and don't need to manually provide any credentials to push  
'''
class AWS_API():
    def __init__(self):
        return None

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
    def start_instances(self, count=1, instance_type='t2.micro'):
        # ami = 'ami-00068cd7555f543d5'  # linux
        ami = 'ami-00a208c7cdba991ea'  # ubuntu
        ec2 = boto3.resource('ec2')
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
        client = boto3.client('ec2')
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
            for row in reader:
                user = row[0]
                email = row[1]
                if not (user and email):
                    continue
                username = re.sub('[^0-9a-zA-Z]+', '', email.split(
                    '@')[0]).lower()
                user_info.append((username, user, email))
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


    # helper function for threading in prepare_machine_environments()
    def run_setup_command(self, command):
        print(command)
        os.system(command)


    # once you've run start_instances(), ssh into the machines to set up clone the repo, set up conda environments, etc.
    def prepare_machine_environments(self, password):
        hosts = [str(ip_address) for _, _, ip_address, _ in self.get_instance_info() if ip_address is not None]
        here = os.getcwd()
        credential_path = os.path.join(here, 'ec2-keypair.pem')
        student_groups = self.assign_students_to_machines()
        student_groups_and_hosts = zip(student_groups, hosts)
        commands = list()
        for student_group, host in student_groups_and_hosts:
            setup_command = 'sudo python3 machine_learning_aws/setup.py --users %s --pwd %s' % (student_group, password)
            clone_command = '"git clone https://github.com/julianalverio/machine_learning_aws.git && %s"' % setup_command
            ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no" ubuntu@%s %s' % (credential_path, host, clone_command)
            commands.append(ssh_command)
        threads = list()
        for command in commands:
            thread = threading.Thread(target=self.run_setup_command,
                                      args=(command,))
            threads.append(thread)
        print('Now preparing machine environments.')
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

        commands = list()
        student_groups_and_hosts = zip(student_groups, hosts)
        counter = 0  # Begin counter at zero
        for student_group, host in student_groups_and_hosts:
            setup_command = 'sudo python3 setup2.py --users %s ' \
                            '--port_counters %s' % (student_group, counter)
            ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no" ubuntu@%s %s' % (credential_path, host, setup_command)
            commands.append(ssh_command)
            counter += 1  # Increment counter for remote porting
        threads = list()
        for command in commands:
            thread = threading.Thread(target=self.run_setup_command,
                                      args=(command,))
            threads.append(thread)
        print('Now building conda environments')
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

        print('Done! This print statement does not guarantee success.')


    def mail_to_list(self):
        # Get user info from method above
        user_info = self.get_user_info()
        N = len(user_info)

        # Get usernames, names, and emails
        usernames = [user_info[i][0] for i in range(N)]
        names = [user_info[i][1] for i in range(N)]
        emails = [user_info[i][2] for i in range(N)]

        # Get instance info
        #instance_info =

        # Iterate through usernames, names, and emails
        port_counter = 0
        for uname, name, email_addr in zip(usernames, names, emails):
            fromaddr = "machinelearning.uruguay@gmail.com"
            toaddr = email_addr
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Daily Log In Information"
            #body = "Test mail from python"
            body = """\
            
            Dear %s,
            
            Below is your login information for this course.  Please
            copy and paste the following command into your command line (for 
            Windows Users, use Git Bash:
            
            ssh -i ec2-keypair.pem -NfL %s:localhost:8888 %s@IP
           
            
            Sending this command will take you to your assigned AWS EC2 
            instance.  From here, you can view your Jupyter notebooks for 
            this course by navigating to your local browser (Chrome is 
            preferred), and typing:
            
            localhost:8888.
            
            This will take you to the Jupyter notebooks on AWS that we will 
            be using for the rest of this course!
            
            If you have any technical issues or difficulties with this, please 
            let us know and we will be happy to help resolve them.  
            
            Muchas gracias,
            GSL Uruguay Technical Team
            """ % (name, port_counter, uname, )

            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(fromaddr, "support_vector_machine")
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()

            # Increment port counter by 1 for each user
            port_counter += 1


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

def main_debugging():
    API = AWS_API()
    print(API.get_user_info())

    API.terminate_instances()
    API.start_instances(count=2, instance_type='m5a.large')
    time.sleep(10)  # TODO: Might not need this
    API.get_instance_info()
    #API.prepare_machine_environments('test')

def main():
    """Main script for running startup of AWS instances."""
    API = AWS_API()  # Instantiate class object
    API.terminate_instances()
    API.start_instances(count=1, instance_type='m5a.large')
    time.sleep(10)  #TODO: Might not need this
    API.prepare_machine_environments('test')


if __name__=="__main__":
    main_debugging()

