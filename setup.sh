#!/bin/bash

git -C /home/ubuntu/machine_learning_aws pull
cp -r /home/ubuntu/machine_learning_aws/template /home/ubuntu/machine_learning_aws/daily_user
tmux new-session -d 'conda activate conda_env && jupyter notebook --port=8888 --no-browser --ip="*" --NotebookApp.token="" --NotebookApp.password="" /home/ubuntu/machine_learning_aws/daily_user'



