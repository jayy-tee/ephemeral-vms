#!/bin/bash

aws s3 cp s3://${bucket_name}/ec2-scripts.zip .
unzip ec2-scripts.zip

sudo bash ec2-scripts/create-azpagent-user.sh
sudo cp ec2-scripts/* /home/azpagent/
sudo su -c "bash install-azpagent.sh" - azpagent

cd /home/azpagent
sudo bash svc.sh install azpagent
sudo bash svc.sh start