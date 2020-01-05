cd ~/machine_learning_aws
./Miniconda3-latest-Linux-x86_64.sh -p /home/ubuntu/conda -b
cp .condarc ~/.condarc
cd ~
./conda/bin/conda init
source ~/.bashrc
cd ~/machine_learning_aws
conda env create -f environment.yml -n test  # modularize this!
conda activate test
