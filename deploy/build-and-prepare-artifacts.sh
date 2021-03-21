#!/bin/sh

## Prepare Python Deps
python3 -m venv ../lambda/.venv
source ../lambda/.venv/bin/activate
pip3 install requests boto3
deactivate

## Add python deps to "deployment-package.zip"
pushd ../lambda/.venv/lib/python3.8/site-packages
zip -r ../../../../../deploy/deployment-package.zip .
popd

## Add Lambda function to "deployment-package.zip"
pushd ../lambda
zip -g ../deploy/deployment-package.zip *.py
popd

## Bundle EC2 Scripts
pushd ../
zip -r deploy/ec2-scripts.zip ec2-scripts/
popd