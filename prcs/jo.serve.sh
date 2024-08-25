#!/bin/bash

# Regular Colors
BLACK="\[\033[0;30m\]"        # Black
RED="\[\033[0;31m\]"          # Red
GREEN="\[\033[0;32m\]"        # Green
YEL="\[\033[0;33m\]"       # Yellow
BLUE="\[\033[0;34m\]"         # Blue
PURPLE="\[\033[0;35m\]"       # Purple
CYAN="\[\033[0;36m\]"         # Cyan
WHITE="\[\033[0;37m\]"        # White
NC='\033[0m' # No Color

source /etc/environment
cd /home/$USERNAME/python_venvs/libs/altered
pipenv run jo serve -n digiserver -rt
