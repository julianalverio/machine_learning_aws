import boto3
from pprint import pprint
import time

# reference: https://stackabuse.com/automating-aws-ec2-management-with-python-and-boto3/


def get_session(region):
    return boto3.session.Session(region_name=region)


def generate_keypair():
    ec2 = boto3.resource('ec2')
    outfile = open('ec2-keypair.pem', 'w')
    key_pair = ec2.create_key_pair(KeyName='ec2-keypair')
    KeyPairOut = str(key_pair.key_material)
    print(KeyPairOut)
    outfile.write(KeyPairOut)


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


def get_instances():
    ec2 = boto3.resource('ec2')
    instances = list()
    for instance_id, _, _, _ in get_instance_info():
        instances.append(ec2.Instance(instance_id))
    return instances


def wait_for_instances(target_states=['running']):
    for target_state in target_states:
        assert target_state in ['pending', 'running', 'stopping', 'stopped', 'shutting-down', 'terminated']
    instances = get_instances()
    states = [instance.state['Name'] for instance in instances]
    ready = all([state in target_states for state in states])
    while not ready:
        print('Waiting for instances to reach %s state. Current states: %s' % (target_state, sorted(states)))
        time.sleep(10)
        instances = get_instances()
        states = [instance.state['Name'] for instance in instances]
        ready = all([state in target_states for state in states])
    print('Instances are ready!')


def stop_instances():
    instances = get_instances()
    for instance in instances:
        try:
            instance.stop()
        except:
            pass
    wait_for_instances(['stopped', 'terminated'])


def write_ip_addresses():
    hosts = [str(ip_address) for _, _, ip_address, _ in get_instance_info() if ip_address is not None]
    hosts = '\n'.join(hosts)
    with open('hosts.txt', 'w+') as f:
        f.write(hosts)




# start_instances(count=2, instance_type='m5a.large')
write_ip_addresses()