#!/bin/bash

# Source muOS functions if available
if [ -f /opt/muos/script/var/func.sh ]; then
    . /opt/muos/script/var/func.sh
else
    echo "Warning: muOS functions not found"
fi

# Signal that we're launching an app
echo app >/tmp/act_go

# Set up SDL scaler if available
if type GET_VAR >/dev/null 2>&1; then
    SDL_HQ_SCALER="$(GET_VAR "device" "sdl/scaler")"
    export SDL_HQ_SCALER
fi

# Get the application directory
APP_DIR="$(dirname "$0")"
cd "$APP_DIR" || exit 1

# Set foreground process if available
if type SET_VAR >/dev/null 2>&1; then
    SET_VAR "system" "foreground_process" "PyLauncher"
fi

# Create a log file for debugging
LOG_FILE="$APP_DIR/PyLauncher.log"
echo "Starting PyLauncher at $(date)" > "$LOG_FILE"

# Make sure Python script is executable
chmod 755 ./main.py

. /mnt/mod/ctrl/configs/functions &>/dev/null 2>&1
progdir=$(cd "$(dirname "$0")"; pwd)

program="python3 ${progdir}/App/main.py"
log_file="${progdir}/log.txt"

python3 App/main.py 2>> "$LOG_FILE"
# Clean up
if [ -n "$SDL_HQ_SCALER" ]; then
    unset SDL_HQ_SCALER
fi

[ "$(GET_VAR "global" "settings/hdmi/enabled")" -eq 1 ] && SCREEN_TYPE="external" || SCREEN_TYPE="internal"
FB_SWITCH "$(GET_VAR "device" "screen/$SCREEN_TYPE/width")" "$(GET_VAR "device" "screen/$SCREEN_TYPE/height")" 32

exit 0