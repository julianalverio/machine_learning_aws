"""Helper script for running remote set up of AWS machines.  The system
commands contained within this script are read and used to install Anaconda (
MiniConda) and create an Anaconda environment."""

# Native Python imports
import argparse
import os
import fileinput
import sys


# Create helper functions for the function "run_setup".


def create_password_text_file(password):
    """Function for creating a password text file and writing this file to
    '/home/ubuntu/set_password.txt'.
    """

    input_str = '%s\n%s\n' % (password, password)
    with open('/home/ubuntu/set_password.txt', 'w+') as f:
        f.write(input_str)


def run_setup():
    """Function that is called inside each remote AWS EC2 instance. Note the
    print statements below are simply used to monitor progress for
    configuring each AWS instance"""

    create_password_text_file('pantalones')
    os.system('cat /home/ubuntu/set_password.txt | sudo passwd ubuntu')
    os.system('sudo service sshd restart')


def main():
    """Main Python function for this script.
    """

    run_setup()

if __name__ == '__main__':
    main()

