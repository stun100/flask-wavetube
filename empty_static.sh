#!/bin/bash

# Get the directory of the script
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Path to the static folder
static_folder="$script_dir/static"

# Check if the static folder exists
if [ -d "$static_folder" ]; then
    # Delete the contents of the static folder
    rm -r "$static_folder"/*

    echo "Contents of $static_folder deleted."
else
    echo "Static folder does not exist."
fi
