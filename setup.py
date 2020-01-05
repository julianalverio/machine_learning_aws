import argparse
import os


def create_user_text_file(password):
    input_str = '%s\n%s\n\n\n\n\n\ny\n' % (password, password)
    with open('create_user.txt', 'w+') as f:
        f.write(input_str)


def create_users(users_str):
    users = users_str.split(',')
    for user in users:
        create_user_cmd = 'cat create_user.txt | sudo adduser %s' % user
        os.system(create_user_cmd)


def run_setup():
    setup_cmd = 'bash setup.bash'
    os.system(setup_cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--users', type=str)
    parser.add_argument('--pwd', type=str)
    args = parser.parse_args()
    create_user_text_file(args.pwd)
    create_users(args.users)
    run_setup()
