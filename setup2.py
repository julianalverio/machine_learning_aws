# import os
# import argparse
#
# def run_setup2():
#     """This function is run individually on each Amazon machine.  aws_api.py
#     iteratively calls each function on each machine as each AWS machine is
#     ssh'ed into."""
#
#     # for user, port_index in zip(users, port_indices):
#     # Build conda environment
#     os.system('conda env create -f environment.yml -n conda_env')
#
#     # Now we want to activate the conda environment
#     os.system('conda activate conda_env')
#
#     # Start Jupyter notebooks
#     port_number = 8888
#     os.system('jupyter notebook --no-browser --port=%s /home/ubuntu/machine_learning_aws/daily_user' % port_number)
#
#
# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--users', type=str)
#     parser.add_argument('--port_counters', type=str)
#     # users, port_numbers = parser.parse_args()
#     run_setup2()
#
#
# if __name__ == '__main__':
#     main()


import os

# ip_address = '3.84.83.86'
# jupyter_command = 'jupyter notebook --no-browser --port=8888 /home/ubuntu/machine_learning_aws/daily_user'
# activate_command = '. /home/ubuntu/conda/bin/conda activate conda_env && %s' % jupyter_command
# build_command = '. /home/ubuntu/conda/bin/conda env create -f /home/ubuntu/machine_learning_aws/environment.yml -n conda_env && %s' % activate_command
# ls_command = 'ls ~ && %s' % build_command
# source_command = 'source /home/ubuntu/.bashrc && %s' % ls_command
# ssh_command = 'ssh -i /Users/julianalverio/code/machine_learning_aws/ec2-keypair.pem ubuntu@%s %s' % (ip_address, source_command)


cmd = 'ssh -i /Users/julianalverio/code/machine_learning_aws/ec2-keypair.pem ubuntu@3.84.83.86 "source /home/ubuntu/.bashrc && . export PATH=/home/ubuntu/conda/bin/conda:$PATH && env list"'
os.system(cmd)



'''
ssh -o "StrictHostKeyChecking no" ubuntu@'3.84.83.86'
source ~/.bashrc
sudo conda env create -f /home/ubuntu/machine_learning_aws/environment.yml -n conda_env
conda activate conda_env
jupyter
'''


