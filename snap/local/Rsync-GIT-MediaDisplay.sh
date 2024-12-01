#!/bin/bash
# Script to sync Windows folder with local folder

# Define paths (modify these as needed)
MOUNTED_WINDOWS_FOLDER="/media/sf_GitHub/MediaDisplay-MPV/"
LOCAL_FOLDER="$HOME/Documents/GIT-Sync/Linux-MediaDisplay/"

# Sync command using rsync
rsync -av --delete "$MOUNTED_WINDOWS_FOLDER" "$LOCAL_FOLDER"

## Run Unison for synchronization
#unison "$MOUNTED_WINDOWS_FOLDER" "$LOCAL_FOLDER"

echo "Sync completed successfully."

