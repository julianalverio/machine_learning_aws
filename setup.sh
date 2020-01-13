#!/bin/bash

cp -r /home/ubuntu/machine_learning_aws/template /home/ubuntu/machine_learning_aws/daily_user
tmux new -d -s jupyter
tmux send-keys -t jupyter.0 'conda activate conda_env && jupyter notebook --port=8888 --no-browser --ip="*" --NotebookApp.token="" --NotebookApp.password="" /home/ubuntu/machine_learning_aws/daily_user' ENTER
