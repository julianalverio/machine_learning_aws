# This is where setup2.py began

ip_address = '3.84.83.86'
jupyter_command = 'jupyter notebook --no-browser --port=8888' \
'/home/ubuntu/machine_learning_aws/daily_user'
activate_command = '. /home/ubuntu/conda/bin/conda activate conda_env' \
'&& %s' % jupyter_command
build_command = '. /home/ubuntu/conda/bin/conda env create -f' \
'/home/ubuntu/machine_learning_aws/environment.yml -n conda_env && %s' %
source_command = 'source ~/.bashrc && %s' % build_command
ssh_command = 'ssh ubuntu@%s %s' % (ip_address, source_command)
os.system(source_command)

os.system('. /home/ubuntu/conda/bin/conda env create -f' \
'/home/ubuntu/machine_learning_aws/environment.yml -n conda_env')
os.system('. /home/ubuntu/conda/bin/conda activate conda_env')
os.system('jupyter notebook --no-browser --port=8888' \
'/home/ubuntu/machine_learning_aws/daily_user')

os.system('sh /home/ubuntu/conda/bin/conda init')
os.system('sh /home/ubuntu/conda/bin/conda init')
os.system('sh /home/ubuntu/conda/bin/conda init bash')
os.system('source /home/ubuntu/.bashrc')
os.system('conda env create -f environment.yml -n conda_env')

# Functions for debugging and creating different users for remote machines
def create_users(users):
    for user in users:
        create_user_cmd = 'cat create_user.txt | sudo adduser %s' % user
        os.system(create_user_cmd)


def create_one_user():
    create_user_cmd = 'cat create_user.txt | sudo adduser %s' % 'bouncy'
    os.system(create_user_cmd)