#!/bin/bash
# Import general functions
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/executioner_funcs.sh

# Make sure the binaries used in this script exist
bin_exists ifconfig
bin_exists grep 

# Main logic
ifconfig | egrep "Link|inet" -B1 | egrep -v "^$"
