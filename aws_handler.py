import pandas as pd
import argparse
import os
import boto3
import re


# first feature: path intake
# second feature: fixes the header issue we had


def generate_keypair():
    """Given that you have properly set up the AWS CLI, this will generate
    the .pem file to call the methods below.  This cannot be done if
    someone else has already """
    ec2 = boto3.resource('ec2')
    key_pair = ec2.create_key_pair(KeyName='julian3')
    KeyPairOut = str(key_pair.key_material)
    with open('ec2-keypair.pem', 'w+') as f:
        f.write(KeyPairOut)
    print("Keypair written")


class Handler(object):
    def __init__(self, path):
        full_path = os.path.join(os.getcwd(), path)
        users = pd.read_csv(full_path, header=0)
        if any(['@' in field for field in list(users)]):
            users = pd.read_csv(full_path, header=None)
            users.columns = ['name', 'email']
        usernames = users['email'].apply(lambda email: re.sub('[^0-9a-zA-Z]+', '', email.split('@')[0]).lower())
        users['username'] = usernames
        print(users.head(3))
        self.users = users

    def start_instances(self, count=1, instance_type='t3a.xlarge',
                        ami_type="ubuntu"):
        """Function for starting new EC2 instances from scratch.  This
        function creates n instances, waits for them to be 'running',
        and writes down the ip addresses in hosts.txt.
        """

        # Choose AMI - by default this is Ubuntu
        ami = 'ami-00a208c7cdba991ea'  # ubuntu

        # Create EC2 object
        ec2 = boto3.resource('ec2', region_name="us-east-1")

        # Now create instances using AMI
        ec2.create_instances(
            ImageId=ami,
            MinCount=count,
            MaxCount=count,
            InstanceType=instance_type,
            KeyName='ec2-keypair'
        )

        ## After creating instances, hang
        # self.wait_for_instances(['running', 'terminated', 'shutting-down'])

    def get_credentials_path(self):
        credential_path = [file for file in os.listdir(os.getcwd()) if file.endswith('.pem')][0]
        full_path = os.path.join(os.getcwd(), credential_path)
        return full_path




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default='users.csv')
    args = parser.parse_args()
    handler = Handler(args.path)
    # print(handler.get_credentials_path())
    # handler.push_button()
    # generate_keypair()
    # handler.start_instances(1)


