#!/bin/bash

sudo sh /home/ubuntu/machine_learning_aws/Miniconda3-latest-Linux-x86_64.sh -p /home/ubuntu/conda -b
cp /home/ubuntu/machine_learning_aws/.condarc /home/ubuntu/.condarc
source ~/.bashrc
conda init
conda init bash
source ~/.bashrc

cp -r /home/ubuntu/machine_learning_aws/template /home/ubuntu/machine_learning_aws/daily_user

echo -e "pantalones\npantalones\n" | sudo passwd ubuntu
sudo cat /etc/ssh/sshd_config | sed 's/PasswordAuthentication no/PasswordAuthentication yes/' > /etc/ssh/sshd_config
sudo service sshd restart

sudo apt install tmux

tmux new-session -d -s "jupyter" 