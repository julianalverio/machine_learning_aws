import os
import argparse

def run_setup2(users, port_numbers):
    """This function is run individually on each Amazon machine.  aws_api.py
    iteratively calls each function on each machine as each AWS machine is
    ssh'ed into."""
    # Parse arguments
    user, port_number =

    # Build conda environment
    os.system('conda env create -f environment.yml -n conda_env')

    # Now we want to activate the conda environment
    os.system('conda activate conda_env')

    # Start Jupyter notebooks
    port_number = 8888 + port_index
    os.system('jupyter notebook --no-browser --port=%s' % port_number)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--users', type=str)
    parser.add_argument('--port_counters', type=str)
    users, port_numbers = parser.parse_args()
    run_setup2(users, port_numbers)

if __name__ == '__main__':
    main()
