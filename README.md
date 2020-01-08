# AWS for Machine Learning
This repository contains infrastructure code for setting up AWS machines, as well as a series of Jupyter notebooks for different classroom users to interact with in their own personal EC2 consoles.

## Jupyter Notebooks for Machine Learning
One of the primary purposes of this repository is to maintain a persistent state for our interactive teaching code base, which includes both template and student-edited Jupyter notebooks.  Instructions for accessing template Jupyter notebooks, student Jupyter notebooks, and data are each discussed individually below:

1. **Jupyter Notebook Templates**: These can be cloned, edited, or modified in the `template/` sub-directory.
2. **Jupyter Notebook Files for Students**: These Jupyter notebooks can be accessed on indiviudal EC2 instances through the `daily_user/` sub-directory in the `machine_learning_aws/` repository, or through the absolute path `/home/ubuntu/machine_learning_aws/daily_user/`.  Each of these `daily_user/` repositories will be specific to each EC2 user.
3. **Data for Students**: Data for this course can be found on the EC2 instances under the `data/` sub-directory in the `machine_learning_aws/` repository, or through the absolute path `/home/ubuntu/machine_learning_aws/data/`.  To avoid placing large datasets on GitHub, many of the datasets for this course will be downloaded separately via the `wget` command within the AWS EC2 instances.

## Installing and Configuring Conda Environment on EC2 Instances
Unfortunately, Python does not support sourcing `.bashrc` files, so this sourcing step is required to be done outside of our Python scripts.  We used the following set of bash commands for each instance to: (1) Source the `.bashrc` file, (2) Create the Anaconda environment `conda_env` using the environment file `environment.yml`, and (3) Start a Jupyter notebook on a specific port that can also be listened to locally.  These instructions are below:

1. Copy and paste this command to ssh into a specific EC2 instance, and if prompted, provide the password you were given:

`ssh -o "StrictHostKeyChecking no" ubuntu@<IP ADDRESS>`

2. Once logged in to the EC2 instance, we can install the conda environment and activate it:

`source ~/.bashrc`

`sudo /home/ubuntu/conda/conda/bin/conda env create -f /home/ubuntu/machine_learning_aws/environment.yml -n conda_env` (copy this last line with the last).

`conda init bash`

`conda activate conda_env`

3. Next, start a Jupyter notebook remotely and map it to the 8888 port:

`jupyter notebook --port=8888 --no-browser --ip='*' --NotebookApp.token='' --NotebookApp.password='' /home/ubuntu/machine_learning_aws/daily_user`

4. The final step, **on a local (not EC2) machine**, is to map your computer port `5005` and map it to the remote `8888` port on the EC2 machine:

 `ssh -NfL 5005:localhost:8888 ubuntu@<IP ADDRESS>`
 
5. From here, you can navigate to your `localhost:5005` port on your **local** web browser.  This enables the user to view their remote Jupyter notebook.

## AWS Infrastruture Overview
We used AWS's API to design an `AWSHandler` class through which we set up individual EC2 instances, as well as install Anaconda and a multitude of packages for our students' computing environment.

We use our `AWSHandler` object as our master script in `aws_api.py`.  This handler object contains a variety of different class methods for setting up and maintaining our AWS infrastructure environment.  Some of these methods include: (1) `start_instances()`, (2) `get_instances()`, (3) `wait_for_instances()`, (4) `terminate_instances()`
(5) `get_user_info()`, (6) `initialize_directories()`, (7) `assign_students_to_machines()`, (8) `prepare_machine_environments()`, (9) `mail_to_list()`.

In turn, these methods make system calls to other startup scripts from this repository, namely: `setup1.py`.

## Credits
Thank you to the MIT GSL and Amazon AWS teams for providing us with Amazon computing resources for this course.






