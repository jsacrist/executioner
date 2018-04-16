#/bin/bash

# PATH definition
export PATH="/root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games"

# Function definitions for the rest of the scripts used in this directory
bin_exists(){
    BIN_NAME=$1
    
    which $BIN_NAME &> /dev/null
    RESULT=$?
    if [ $RESULT -ne 0 ] ; then
        echo "$BIN_NAME is not installed, try installing it with: sudo apt-get install $BIN_NAME"
        exit
    fi
}
