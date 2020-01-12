for _, _, host, _ in self.get_instance_info():
    setup_command = 'sudo python3' \
    '/home/ubuntu/machine_learning_aws/setup0.py --pwd %s' % password
    clone_command = 'git clone' \
    'https://github.com/julianalverio/machine_learning_aws.git &&' \
     "%s"'' % setup_command
    ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no"' \
    'ubuntu@%s %s' % (credential_path, host, clone_command)
    print(ssh_command)
    os.system(ssh_command)

counter = 0  # Begin counter at zero
for _, _, host, _ in self.get_instance_info():
    setup_command = 'sudo python3' \
    '/home/ubuntu/machine_learning_aws/setup2.py --users placeholder' \
    '--port_counters %s' % counter
    ssh_command = 'ssh -i %s -o "StrictHostKeyChecking no"' \
    'ubuntu@%s %s' % (credential_path, host, setup_command)
    print(ssh_command)
    os.system(ssh_command)
    counter += 1  # Increment counter for remote porting
    print('Done! This print statement does not guarantee success.')

# TODO: can we wget this from dropbox or Google Drive or something? + TEST
def transfer_data(self):
    """Class method for transfering data from the AWS machines to the
    local machine where this command is being run from or the remote
    GitHub repository.
    """

    # Set remote destination to be the "daily_user/" sub-directory
    remote_destination = '/home/ubuntu/machine_learning_aws/daily_user/'
    local_source = os.path.join(os.getcwd(), 'PLACEHOLD')  # TODO: edit this
    credential_path = os.path.join(os.getcwd(), 'ec2-keypair.pem')

    # Iterate through active EC2 IP addresses
    live_addresses = list()
    for _, _, ip_address, state in self.get_instance_info():
        if state == 'running':
            live_addresses.append(ip_address)

    # Iterate through host names at different IP addresses
    for host in live_addresses:
        scp_command = 'scp -i %s -o "StrictHostKeyChecking no" %s ' \
                      'ubuntu@%s:/home/ubuntu/machine_learning_aws/  %s' % (
                          credential_path, local_source, host,
                          remote_destination)
        scp_command = 'scp -i %s -o "StrictHostKeyChecking no" %s ' \
                      'ubuntu@%s:/home/ubuntu/machine_learning_aws/  %s' % (
                          credential_path, local_source, host,
                          remote_destination)