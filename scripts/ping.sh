#!/bin/bash
# Import general functions
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/executioner_funcs.sh

# Make sure the binaries used in this script exist
bin_exists ping

# Main logic
ping -c5 google.com 2>&1

