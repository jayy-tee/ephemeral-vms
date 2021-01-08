#!/bin/bash

echo "Gathering EC2 instance data..."
EC2_INSTANCE_ID="`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`"
EC2_INSTANCE_REGION="`wget -q -O - http://169.254.169.254/latest/dynamic/instance-identity/document | python extract-instance-region.py`"
export AWS_DEFAULT_REGION=$EC2_INSTANCE_REGION

echo "Setting AWS Settings"
AZP_URL="`aws ssm get-parameter --name azdevops.url --output text | cut -f7`"
AZP_TOKEN="`aws ssm get-parameter --with-decryption --name azdevops.agentregistration.token --output text | cut -f7`"
AZP_TOKEN_B64="`echo -n $AZP_TOKEN: | base64`"
AZP_AGENT_INSTALLDIR="/home/azpagent"
AZP_AGENT_POOL="`aws ec2 describe-tags --filters "Name=resource-id,Values=$EC2_INSTANCE_ID" "Name=key,Values=AzDevOps-Environment" --output=text | cut -f5`"
AZP_AGENT_USER="azpagent"
AZP_PROJECT_NAME="`aws ec2 describe-tags --filters "Name=resource-id,Values=$EC2_INSTANCE_ID" "Name=key,Values=AzDevOps-Project" --output=text | cut -f5`"
AZP_RESOURCE_TAGS="`aws ec2 describe-tags --filters "Name=resource-id,Values=$EC2_INSTANCE_ID" "Name=key,Values=AzDevOps-Environment-ResourceTags" --output=text | cut -f5`"
echo "Detected Azure DevOps Environment Resource Tags $AZP_RESOURCE_TAGS"

echo "Downloading Azure Pipelines Agent..."
case `uname -m` in
        x86_64)
                PLATFORM="linux-x64"
                echo ".. x86_64 architecture detected, using $PLATFORM"
                ;;
        *)
                echo "Could not establish Az Agent platform from processor architecture"
                ;;
esac

PACKAGE_URL="$AZP_URL/_apis/distributedtask/packages/agent?platform=$PLATFORM&\$top=1"
PACKAGES=`curl -s -H "Accept: application/json" -H "Authorization: Basic $AZP_TOKEN_B64" "$PACKAGE_URL"`
DOWNLOAD_URL=`echo $PACKAGES | python extract-azpagent-downloadurl.py`


echo ".. fetching $DOWNLOAD_URL"

if [[ ! -d "$AZP_AGENT_INSTALLDIR" ]]; then
        mkdir $AZP_AGENT_INSTALLDIR
fi

cd $AZP_AGENT_INSTALLDIR
wget -q -O vsts-agent.tar.gz $DOWNLOAD_URL
tar -zxf vsts-agent.tar.gz

if [[ ! -z "$AZP_RESOURCE_TAGS" ]]; then
        ./config.sh \
                --environment \
                --projectname $AZP_PROJECT_NAME \
                --url $AZP_URL \
                --auth pat --token $AZP_TOKEN \
                --environmentname $AZP_AGENT_POOL \
                --agent $EC2_INSTANCE_ID \
                --addvirtualmachineresourcetags \
                --virtualmachineresourcetags $AZP_RESOURCE_TAGS
else
        ./config.sh \
                --environment \
                --projectname $AZP_PROJECT_NAME \
                --url $AZP_URL \
                --auth pat --token $AZP_TOKEN \
                --environmentname $AZP_AGENT_POOL \
                --agent $EC2_INSTANCE_ID
fi

rm $AZP_AGENT_INSTALLDIR/vsts-agent*.tar.gz