#/bin/bash

sudo yum update -y
sudo yum install docker python35 python35-pip -y
sudo gpasswd -a ec2-user docker

sudo curl -L https://github.com/docker/compose/releases/download/1.15.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

sudo pip-3.5 install simple-container-runtime