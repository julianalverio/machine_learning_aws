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