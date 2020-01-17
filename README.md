# AWS for Machine Learning
This repository has a backup of the students' work from the class for the students to view. Each student's code is backed up to student_code/USERNAME, where the USERNAME is everything that comes before the "@" in the student's email address, with any non-english a-z characters deleted, and all characters lowercased. For example, éstuianté!@example.com would find her code under `student_copes/stdudiant`.
The instructor's version of the code is found under `instructor_code/`

This repository also has our infrastructure for setting up EC2 machines each day.


## Jupyter Notebooks for Machine Learning
One of the primary purposes of this repository is to maintain a persistent state for our interactive teaching code base, which includes both template and student-edited Jupyter notebooks.  Instructions for accessing template Jupyter notebooks, student Jupyter notebooks, and data are each discussed individually below:

1. **Jupyter Notebook under `instructor_code`**: These are template for the student to modify.
2. **Jupyter Notebook Files for Students**: We will copy the template notebooks from `instructor_code` to a location where the students can use it every day. For now, the location is `machine_learning_aws/daily_use`, though this location may change as we continue the development of this repository.
3. **Data for Students**: Data for this course can be found on the EC2 instances under the `machine_learning_aws/data/` sub-directory in the `machine_learning_aws/` repository, or through the absolute path `/home/ubuntu/machine_learning_aws/data/`.


## Installing and Configuring Conda Environment on EC2 Instances: Ubuntu AMI
We designed the login and student setup process for these machines to be as straightforward and efficient as possible.  Upon startup of the EC2 instances (when the instances are initialized), a `tmux` session is opened, the conda environment `conda_env` is activated, a `jupyter notebook` command with port assignment is set up, and then the `tmux` session automatically detaches.  This ensures that the Jupyter notebook will continue to run remotely even if there is a loss in ssh connection.

Therefore, the only steps that need to be taken for login are the following (students receive these via email whenever new instances are created):

1. ssh port forwarding (to listen to the remote EC2 Jupyter notebook):

`ssh -o "StrictHostKeyChecking no" -NfL 5005:localhost:8888 ubuntu@<IP_ADDRESS>`

2. In your web browser (e.g. Google Chrome, Safari, Internet Explorer), go to the following:

`localhost:5005`

You should now be able to see the Jupyter notebook interface!  Changes made here are made on the remote EC2 instance, but our team has also built-in functionality in `aws_api.py backup_machines()` for backing up all student work to this GitHub repository, and if/when students are assigned to new instances, work from their user-specific folders is automatically downloaded onto their new assigned EC2 instances.

**NOTE**: If step 1 does not work because "port 5005 is already in use", try killing the port:

a. Mac/Linux users: Type the command `pkill -f 5005`, and repeat step 1.

b. Windows users: Restart/reboot your computer.

## Installing and Configuring Conda Environment on Local Machines:
To provide our students with local access and practice to the machine learning resources/concepts taught in this course, we have also created a framework for our students to work on this code in their own Anaconda environments.  Our team created a distributable Anaconda environment that contains all the necessary Python packages needed for this course called `local_environment.yml`, which can be accessed through this repository.  Users can set up this conda environment and add it to their Jupyter notebook through the following steps:

1. After downloading Anaconda, open an Anaconda prompt (Windows) or a command line (Max/Linux), and change your working directory to the local version of this repository.  From here, follow the OS-agnostic commands below:

2. Create the Anaconda environment in the command line:

`conda env create -f local_env_requirements.txt -n local_env python=3.7`

3. Activate the conda environment:

`conda activate local_env`

4. Install other packages the user may want to have in this Anaconda environment:

`conda install <package_name>` OR `pip install <package_name>` OR `pip3 install <package_name>`

5. In order for users to use the packages in their local environment in a local Jupyter notebook, add the kernel for this environment to `ipython`:

`ipython kernel install --name local_env --user`

The user should already have the packages `ipykernel` and `ipython` installed, but in case running the above command creates errors, make sure these packages are installed via pip:

`pip install ipykernel`

`pip install ipython`

6. Next, open a Jupyter notebook:

`jupyter notebook`

Select any `.ipynb` file, and open it.  Once the notebook is loaded, find the top menu bar, scroll over "kernel".  Find "Change kernel" at the bottom, and the user should then be able to see and select "local_env".  Click on "local_env"; the user's packages from `local_env` should now be import-compatible.

From here, the user can edit/create/delete files in Jupyter.  For future login and use of this Anaconda environment, the user will simply need to open a Jupyter notebook and ensure that the kernel `local_env` is selected.

## Credits
Thank you to the MIT GSL and Amazon AWS Educate teams for providing us with Amazon computing resources for this course.







