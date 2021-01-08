#!/bin/bash

AZP_URL="https://dev.azure.com/jayytee"
AZP_TOKEN="ap5ocillfloerwz6e6ondwtrsldyt5r5nhf4trfgyg7mvxtzosbq"
AZP_TOKEN_B64="`echo -n $AZP_TOKEN: | base64`"
AZP_AGENT_INSTALLDIR="/home/azpagent"
AZP_AGENT_POOL="MyApp-Production"
AZP_AGENT_USER="azpagent"
AZP_PROJECT_NAME="Spikes"

EC2_INSTANCE_ID="`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`"

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
wget -O vsts-agent.tar.gz $DOWNLOAD_URL
tar -zxf vsts-agent.tar.gz

./config.sh \
        --environment \
        --projectname $AZP_PROJECT_NAME \
        --url $AZP_URL \
        --auth pat --token $AZP_TOKEN \
        --environmentname $AZP_AGENT_POOL \
        --agent $EC2_INSTANCE_ID

rm $AZP_AGENT_INSTALLDIR/vsts-agent*.tar.gz