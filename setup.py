"""This allows us to change the password programatically on a fresh AMI boot."""

import os


def create_password_text_file(password):
    """Create a password text file with the appropriate resonses to the passwd command to change the password."""

    input_str = '%s\n%s\n' % (password, password)
    with open('/home/ubuntu/set_password.txt', 'w+') as f:
        f.write(input_str)


def run_setup():
    """This gets called in the EC2 instance so we can change the password."""

    create_password_text_file('pantalones')
    os.system('git -C /home/ubuntu/machine_learning_aws pull')
    os.system('cat /home/ubuntu/set_password.txt | sudo passwd ubuntu')
    os.system('sudo service sshd restart')


if __name__ == '__main__':
    run_setup()

