# ## THIS IS FOR CREATING NEW INSTANCES
# import logging
# import boto3
# from botocore.exceptions import ClientError
#
#
# def create_ec2_instance(image_id, instance_type, keypair_name):
#     """
#     Returns without waiting for the instance to reach
#     a running state.
#
#     :param image_id: ID of AMI to launch, such as 'ami-XXXX'
#     :param instance_type: string, such as 't2.micro'
#     :param keypair_name: string, name of the key pair
#     :return Dictionary containing information about the instance. If error,
#     returns None.
#     """
#
#     # Provision and launch the EC2 instance
#     ec2_client = boto3.client('ec2')
#     try:
#         response = ec2_client.run_instances(ImageId=image_id,
#                                             InstanceType=instance_type,
#                                             KeyName=keypair_name,
#                                             MinCount=1,
#                                             MaxCount=1)
#     except ClientError as e:
#         logging.error(e)
#         return None
#     return response['Instances'][0]
#
#
# def main():
#     """Exercise create_ec2_instance()"""
#
#     # Assign these values before running the program
#     image_id = 'ami-00068cd7555f543d5'  # vanilla linux ami
#     instance_type = 't2.micro'
#     keypair_name = 'ec2-keypair'
#
#     # Set up logging
#     logging.basicConfig(level=logging.DEBUG,
#                         format='%(levelname)s: %(asctime)s: %(message)s')
#
#     # Provision and launch the EC2 instance
#     instance_info = create_ec2_instance(image_id, instance_type, keypair_name)
#     if instance_info is not None:
#         logging.info('Launched EC2 Instance %s' % instance_info["InstanceId"])
#         logging.info('    VPC ID: %s' % instance_info["VpcId"])
#         logging.info('    Private IP Address: %s' % instance_info["PrivateIpAddress"])
#         logging.info('    Current State: %s' % {instance_info["State"]["Name"]})
#
#     import pdb; pdb.set_trace()
#
# if __name__ == '__main__':
#     main()
#
# ## END CREATING NEW INSTANCES


## THIS IS FOR GETTING INFORMATION
# import boto3

# ec2 = boto3.client('ec2')
# response = ec2.describe_instances()
# print(response)
# ## to get the public dns name: response['Reservations'][0]['Instances'][0]['PublicDnsName']

# instance = response['Reservations'][0]['Instances'][0]


# import pdb; pdb.set_trace()


# ## This is for stopping instances
# client = boto3.client('ec2')
# stop_response = client.stop_instances(
#     InstanceIds=[
#         'i-0b5e383b6d8e01b25',
#     ],
#     Hibernate=False,
#     DryRun=False,
#     Force=True
# )
## End stopping instances

# I AM TRYING OUT THE APPROACH FROM https://stackabuse.com/automating-aws-ec2-management-with-python-and-boto3/

import boto3
from pprint import pprint
import time


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



start_instances(count=3)

# wait_for_instances(['running', 'terminated'])



# client = session.client('ec2')
# ec2 = session.resource('ec2')


# generate_keypair()

# pprint.pprint(client.describe_instances())
# create_instances(count=2)

# print(get_instance_info())






