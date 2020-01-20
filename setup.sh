#!/bin/bash

# do this twice, it's unclear which will work
echo -e 'pantalones\npantalones\n' | sudo passwd ubuntu
sudo service sshd restart

echo 'pantalones\npantalones\n' | sudo passwd ubuntu
sudo service sshd restart

# Pull repo upon startup
git -C /home/ubuntu/machine_learning_aws pull


# Move code from template to daily_user
cp -rT /home/ubuntu/machine_learning_aws/instructor_code /home/ubuntu/machine_learning_aws/daily_user

# Start a tmux session
tmux new -d -s jupyter
tmux send-keys -t jupyter.0 '/bin/bash' ENTER
tmux send-keys -t jupyter.0 'conda activate conda_env && jupyter notebook --port=8888 --no-browser --ip="*" --NotebookApp.token="" --NotebookApp.password="" /home/ubuntu/machine_learning_aws/daily_user' ENTER
