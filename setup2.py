import os
import argparse


def run_setup():
    # build conda environment
    os.system('conda env create -f environment.yml -n conda_env')








if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--users', type=str)
    # parser.add_argument('--pwd', type=str)
    args = parser.parse_args()
    run_setup()
