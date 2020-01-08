import os
import argparse

def run_setup2():
    """This function is run individually on each Amazon machine.  aws_api.py
    iteratively calls each function on each machine as each AWS machine is
    ssh'ed into."""

    # for user, port_index in zip(users, port_indices):
    # Build conda environment
    os.system('conda env create -f environment.yml -n conda_env')
    os.system('cd /home/ubuntu/machine_learning_aws/')

    # Now we want to activate the conda environment
    os.system('conda activate conda_env')

    # Start Jupyter notebooks
    port_number = 8888
    os.system('jupyter notebook --no-browser --port=%s /home/ubuntu/machine_learning_aws/daily_user' % port_number)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--users', type=str)
    parser.add_argument('--port_counters', type=str)
    # users, port_numbers = parser.parse_args()
    run_setup2()


if __name__ == '__main__':
    main()
