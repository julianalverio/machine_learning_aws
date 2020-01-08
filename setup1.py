import argparse
import os
import fileinput
import sys


def create_user_text_file(password):
    input_str = '%s\n%s\n\n\n\n\n\ny\n' % (password, password)
    with open('create_user.txt', 'w+') as f:
        f.write(input_str)


def create_users(users):
    for user in users:
        create_user_cmd = 'cat create_user.txt | sudo adduser %s' % user
        os.system(create_user_cmd)


def create_one_user():
    create_user_cmd = 'cat create_user.txt | sudo adduser %s' % 'bouncy'
    os.system(create_user_cmd)


def create_password_text_file(password):
    input_str = '%s\n%s\n' % (password, password)
    with open('/home/ubuntu/set_password.txt', 'w+') as f:
        f.write(input_str)


def replaceAll(file, searchExp, replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp, replaceExp)
        sys.stdout.write(line)


def run_setup(password):
    create_password_text_file(password)
    os.chdir('/home/ubuntu/machine_learning_aws')
    print('I AM INSTALLING CONDA')
    os.system('sudo sh /home/ubuntu/machine_learning_aws/Miniconda3-latest-Linux-x86_64.sh -p /home/ubuntu/conda -b')
    print('SWAPPING CONDARC')
    os.system('cp /home/ubuntu/machine_learning_aws/.condarc /home/ubuntu/.condarc')
    print('SETTING UP DAILY USER FILES')
    os.system('cp -r /home/ubuntu/machine_learning_aws/template /home/ubuntu/machine_learning_aws/daily_user')
    os.chdir('/home/ubuntu')
    print('DOING CONDA INIT')
    os.chdir('/home/ubuntu/')
    os.system('./conda/bin/conda init')
    os.system('./conda/bin/conda init bash')
    print('CHANGING UBUNTU PASSWORD')
    os.system('cat /home/ubuntu/set_password.txt | sudo passwd ubuntu')
    print('SWAPPING THE SSH CONFIG FILE')
    replaceAll("/etc/ssh/sshd_config", "PasswordAuthentication no", "PasswordAuthentication yes")
    print('RESTARTING SSH SERVICE')
    os.system('sudo service sshd restart')


    # this is where setup2.py began

    ip_address = '3.84.83.86'
    jupyter_command = 'jupyter notebook --no-browser --port=8888 /home/ubuntu/machine_learning_aws/daily_user'
    activate_command = '. /home/ubuntu/conda/bin/conda activate conda_env && %s' % jupyter_command
    build_command = '. /home/ubuntu/conda/bin/conda env create -f /home/ubuntu/machine_learning_aws/environment.yml -n conda_env && %s' % activate_command
    source_command = 'source ~/.bashrc && %s' % build_command
    ssh_command = 'ssh ubuntu@%s %s' % (ip_address, source_command)
    os.system(source_command)

    # os.system('. /home/ubuntu/conda/bin/conda env create -f /home/ubuntu/machine_learning_aws/environment.yml -n conda_env')
    # os.system('. /home/ubuntu/conda/bin/conda activate conda_env')
    # os.system('jupyter notebook --no-browser --port=8888 /home/ubuntu/machine_learning_aws/daily_user')


    # os.system('sh /home/ubuntu/conda/bin/conda init')
    # os.system('sh /home/ubuntu/conda/bin/conda init')
    # os.system('sh /home/ubuntu/conda/bin/conda init bash')
    # os.system('source /home/ubuntu/.bashrc')
    # os.system('conda env create -f environment.yml -n conda_env')
    print('I finished the setup python script!')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--users', type=str)
    parser.add_argument('--pwd', type=str)
    args = parser.parse_args()
    # create_user_text_file(args.pwd)
    # create_one_user()
    # users = args.users.split(',')
    # create_users(users)
    run_setup(args.pwd)

if __name__ == '__main__':
    main()