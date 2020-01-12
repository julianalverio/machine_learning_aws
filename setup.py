"""Helper script for running remote set up of AWS machines.  The system
commands contained within this script are read and used to install Anaconda (
MiniConda) and create an Anaconda environment."""

# Native Python imports
import argparse
import os
import fileinput
import sys


# Create helper functions for the function "run_setup".

def create_user_text_file(password):
    """Function for creating a user text file and writing this file to
    'create_user.txt'
    """

    input_str = '%s\n%s\n\n\n\n\n\ny\n' % (password, password)
    with open('create_user.txt', 'w+') as f:
        f.write(input_str)
        f.close()


def create_password_text_file(password):
    """Function for creating a password text file and writing this file to
    '/home/ubuntu/set_password.txt'.
    """

    input_str = '%s\n%s\n' % (password, password)
    with open('/home/ubuntu/set_password.txt', 'w+') as f:
        f.write(input_str)


def replaceAll(file, searchExp, replaceExp):
    """Code for replacing text lines in file containing searchExp with
    replaceExp.  The new file overrides the previous file.
    """

    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp, replaceExp)
        sys.stdout.write(line)


def run_setup(password, custom_ami=False):
    """Function that is called inside each remote AWS EC2 instance. Note the
    print statements below are simply used to monitor progress for
    configuring each AWS instance"""

    # Only do the following if setting up instance from scratch
    if not custom_ami:
        # Create a .txt file for passwords
        create_password_text_file(password)
        os.chdir('/home/ubuntu/machine_learning_aws')

        # Anaconda installation
        print('I AM INSTALLING CONDA')
        os.system(
            'sudo sh /home/ubuntu/machine_learning_aws/Miniconda3-latest-Linux'
            '-x86_64.sh -p /home/ubuntu/conda -b')

        # Swap the condarc
        print('SWAPPING CONDARC')
        os.system(
            'cp /home/ubuntu/machine_learning_aws/.condarc /home/ubuntu/.condarc')

        # Set up daily user files that can later be retrieved for saving work
        print('SETTING UP DAILY USER FILES')
        os.system(
            'cp -r /home/ubuntu/machine_learning_aws/template '
            '/home/ubuntu/machine_learning_aws/daily_user')
        os.chdir('/home/ubuntu')

        # Initializing conda
        print('DOING CONDA INIT')
        os.chdir('/home/ubuntu/')
        os.system('./conda/bin/conda init')
        os.system('./conda/bin/conda init bash')

    # Changing ubuntu password (to common password for entire class)
    print('CHANGING UBUNTU PASSWORD')
    os.system('cat /home/ubuntu/set_password.txt | sudo passwd ubuntu')

    # Modify sshd configuration file
    print('SWAPPING THE SSH CONFIG FILE')
    replaceAll("/etc/ssh/sshd_config", "PasswordAuthentication no",
               "PasswordAuthentication yes")

    # Restart for changes to take effect
    print('RESTARTING SSH SERVICE')
    os.system('sudo service sshd restart')

    # Notify us when finished
    print('I finished the setup python script!')

def main():
    """Main Python function for this script.
    """

    # Create an argument parser.  Commands iteratively come from aws_api.py
    parser = argparse.ArgumentParser()
    parser.add_argument('--pwd', type=str, help="String password used for ssh "
                                                "login into instance")
    parser.add_argument('--custom_ami', type=bool, help="Boolean flag for "
                                                "whether or not we use a custom"
                                                "AMI. If you do not know what "
                                                 "this means, you should "
                                                 "probably set equal to False.")
    args = parser.parse_args()

    # Run setup command for instance - note this depends on AMI we use
    run_setup(args.pwd, custom_ami=args.custom_ami)

if __name__ == '__main__':
    main()

