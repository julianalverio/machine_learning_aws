# Give write permissions for Jupyter notebook
sudo chmod -R 777 /home/ubuntu/machine_learning_aws/daily_user/

# Start tmux session
tmux

# Next activate conda environment
conda activate conda_env

# Now start Jupyter notebook at port 8888
jupyter notebook --port=8888 --no-browser --ip='*' --NotebookApp.token='' --NotebookApp.password='' /home/ubuntu/machine_learning_aws/daily_user

