#!/bin/bash
COLORIZE="/mnt/c/Users/and_p/Dropbox/src/Python/colorize/colorize.py"
LOCAL_BIN="/usr/local/bin/colorize"

rcp $COLORIZE root@192.168.168.112:$LOCAL_BIN
rcp $COLORIZE root@192.168.168.121:$LOCAL_BIN
#rcp $COLORIZE root@192.168.168.192:$LOCAL_BIN
#rcp $COLORIZE root@192.168.168.193:$LOCAL_BIN
rcp $COLORIZE aru@192.168.168.71:$LOCAL_BIN
rcp $COLORIZE root@192.168.168.76:$LOCAL_BIN
rcp $COLORIZE root@192.168.168.81:$LOCAL_BIN
rcp $COLORIZE root@192.168.168.82:$LOCAL_BIN
#rcp $COLORIZE aru@telegit:$LOCAL_BIN
