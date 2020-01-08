import argparse
import os


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
    with open('set_password.txt', 'w+') as f:
        f.write(input_str)

def run_setup():
    os.chdir('/home/ubuntu/machine_learning_aws')
    os.system('sh /home/ubuntu/machine_learning_aws/Miniconda3-latest-Linux-x86_64.sh -p /home/ubuntu/conda -b')
    os.system('cp /home/ubuntu/machine_learning_aws/.condarc /home/ubuntu/.condarc')
    os.system('cp -r /home/ubuntu/machine_learning_aws/template /home/ubuntu/machine_learning_aws/daily_user')
    os.chdir('/home/ubuntu')
    os.system('./conda/bin/conda init')
    os.system('./conda/bin/conda init bash')
    os.system('sudo passwd ubuntu')
    os.system('sudo service sshd restart')
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