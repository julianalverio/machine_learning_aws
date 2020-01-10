import os
import argparse


def create_user_text_file(password):
    input_str = '%s\n%s\n\n\n\n\n\ny\n' % (password, password)
    with open('create_user.txt', 'w+') as f:
        f.write(input_str)


def create_one_user():
    create_user_cmd = 'cat create_user.txt | sudo adduser %s' % 'bouncy'
    os.system(create_user_cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pwd', type=str)
    args = parser.parse_args()
    create_user_text_file(args.pwd)
    create_one_user()
