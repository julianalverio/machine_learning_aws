import boto3
from pprint import pprint
import time
import os
import csv
import re
import math
import threading

# reference: https://stackabuse.com/automating-aws-ec2-management-with-python-and-boto3/
'''
Assumptions about this directory:
1. There is a file named ec2-keypair.pem
2. There is folder named template which has all the jupyter notebooks for the class
3. There is a file named email_credentials.txt which has the password for the bot gmail address
4. There is a file users.csv where the first column is full names and the second is email addresses for students
5. You are a collabotor on the machine_learning_aws repo and don't need to manually provide any credentials to push  
'''


# Given that you have properly set up the AWS CLI, this will generate the .pem file to call the methods below
def generate_keypair():
    ec2 = boto3.resource('ec2')
    outfile = open('ec2-keypair.pem', 'w')
    key_pair = ec2.create_key_pair(KeyName='ec2-keypair')
    KeyPairOut = str(key_pair.key_material)
    print(KeyPairOut)
    outfile.write(KeyPairOut)


# Create n instances, wait for them to be 'running', and write down the ip addresses in hosts.txt
def start_instances(count=1, instance_type='t2.micro'):
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
    wait_for_instances(['running', 'terminated'])


# returns a list of [instance_id, instance_type, ip_address, current_state] lists.
def get_instance_info():
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
def get_instances():
    ec2 = boto3.resource('ec2')
    instances = list()
    for instance_id, _, _, _ in get_instance_info():
        instances.append(ec2.Instance(instance_id))
    return instances


# wait for all the instances to be in a desired set of states. Retry every 10 seconds.
def wait_for_instances(target_states=['running']):
    for target_state in target_states:
        assert target_state in ['pending', 'running', 'stopping', 'stopped', 'shutting-down', 'terminated']
    instances = get_instances()
    states = [instance.state['Name'] for instance in instances]
    ready = all([state in target_states for state in states])
    while not ready:
        print('Waiting for instances to reach %s states. Current states: %s' % (target_states, sorted(states)))
        time.sleep(10)
        instances = get_instances()
        states = [instance.state['Name'] for instance in instances]
        ready = all([state in target_states for state in states])
    print('Instances are ready!')


# Terminate all the instanes
def terminate_instances():
    instances = get_instances()
    for instance in instances:
        try:
            instance.terminate()
        except:
            pass
    wait_for_instances(['terminated'])


# Read from users.csv. Generate usernames by removing alphanumeric characters from their email username
# Return list of (username, user's full name, email address) tuples
def get_user_info():
    with open('users.csv', 'r') as f:
        reader = csv.reader(f)
        user_info = list()
        for row in reader:
            user = row[0]
            email = row[1]
            if not (user and email):
                continue
            username = re.sub('[^0-9a-zA-Z]+', '', email.split('@')[0])
            user_info.append((username, user, email))
    return user_info


# You only run this once at the beginning of the course
# Generate a directory with code notebooks for each user.
def initialize_directories():
    usernames = [username for username, _, _ in get_user_info()]
    for username in usernames:
        cmd = 'cp -r template users/%s' % username
        os.system(cmd)


# Once you have run start_instances() and the machines are running, partition the students equally among the machines.
def assign_students_to_machines():
    user_info = get_user_info()  # username, user, email
    num_students = len(user_info)
    num_machines = len([state for _, _, _, state in get_instance_info() if state == 'running'])
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
def run_setup_command(command):
    print(command)
    os.system(command)


# once you've run start_instances(), ssh into the machines to set up clone the repo, set up conda environments, etc.
def prepare_machine_environments(password):
    hosts = [str(ip_address) for _, _, ip_address, _ in get_instance_info() if ip_address is not None]
    here = os.getcwd()
    credential_path = os.path.join(here, 'ec2-keypair.pem')
    student_groups = assign_students_to_machines()
    student_groups_and_hosts = zip(student_groups, hosts)
    commands = list()
    for student_group, host in student_groups_and_hosts:
        setup_command = 'sudo python3 machine_learning_aws/setup.py --users %s --pwd %s' % (student_group, password)
        clone_command = '"git clone https://github.com/julianalverio/machine_learning_aws.git && %s"' % setup_command
        ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no" ubuntu@%s %s' % (credential_path, host, clone_command)
        commands.append(ssh_command)
    threads = list()
    for command in commands:
        thread = threading.Thread(target=run_setup_command, args=(command,))
        threads.append(thread)
    print('Now preparing machine environments.')
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    print('Done! This print statement does not guarantee success.')


# this needs to be tested
def backup_machines():
    live_addresses = list()
    for _, _, ip_address, state in get_instance_info():
        if state == 'running':
            live_addresses.append(ip_address)
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
def transfer_data():
    remote_destination = '/home/ubuntu/machine_learning_aws/'  # TODO: edit this
    local_source = os.path.join(os.getcwd(), 'something')  # TODO: edit this
    credential_path = os.path.join(os.getcwd(), 'ec2-keypair.pem')
    live_addresses = list()
    for _, _, ip_address, state in get_instance_info():
        if state == 'running':
            live_addresses.append(ip_address)
    for host in live_addresses:
        scp_command = 'scp -i %s -o "StrictHostKeyChecking no" %s ubuntu@%s:/home/ubuntu/machine_learning_aws/  %s' % (credential_path, local_source, host, remote_destination)
        os.system(scp_command)


# prepare_machine_environments('test')
# start_instances(count=1, instance_type='m5a.large')
prepare_machine_environments('test')
# terminate_instances()

