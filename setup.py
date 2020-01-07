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


def run_setup():
    os.chdir('/home/ubuntu/machine_learning_aws')
    os.system('sh /home/ubuntu/machine_learning_aws/Miniconda3-latest-Linux-x86_64.sh -p /home/ubuntu/conda -b')
    os.system('cp /home/ubuntu/machine_learning_aws/.condarc /home/ubumtu/.condarc')
    os.system('sh /home/ubuntu/conda/bin/conda init')
    os.system('sh /home/ubuntu/conda/bin/conda init bash')
    os.system('source /home/ubuntu/.bashrc')
    os.system('conda env create -f environment.yml -n conda_env')
    print('I finished the setup python script!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--users', type=str)
    parser.add_argument('--pwd', type=str)
    args = parser.parse_args()
    create_user_text_file(args.pwd)
    users = args.users.split(',')
    create_users(users)
    run_setup()
