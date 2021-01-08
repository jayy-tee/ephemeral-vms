#!/bin/bash

AZP_AGENT_INSTALLDIR="/home/azpagent"
AZP_AGENT_USER="azpagent"

id -u $AZP_AGENT_USER &>/dev/null || adduser $AZP_AGENT_USER

echo "$AZP_AGENT_USER  ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/$AZP_AGENT_USER
