#!/bin/bash
# Import general functions
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/executioner_funcs.sh

# Make sure the binaries used in this script exist
bin_exists linuxlogo
bin_exists uptime

# Main logic
linuxlogo -a | tr "<" "/"

UPTIME=$(uptime)
echo -e -n "$UPTIME" "(1, 5, 15 minutes)\n\n"

FIRMWARE_VER=$(vcgencmd version 2>/dev/null)
FWV_RETVAL=$?

if [ $FWV_RETVAL == 0 ]; then
    echo "Raspberry pi firmware:"
    echo "$FIRMWARE_VER"

    echo ""
    LS_SCR=$(runuser -l pi -c 'screen -ls')
    echo "$LS_SCR"
else
    echo "Not running on a raspberry pi"
fi


