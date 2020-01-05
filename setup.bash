cd ~/machine_learning_aws
./Miniconda3-latest-Linux-x86_64.sh -p /home/ubuntu/conda -b
cp .condarc ~/.condarc
source ~/.bashrc
conda env create -f environment.yml -n test  # fix this!
