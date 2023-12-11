#!/bin/bash

# Specify the base directory
base_directory="/Users/anushkrishnav/Documents/Projects/DevGPT"
# Initialize PYTHONPATH
PYTHONPATH=""

# Find immediate subdirectories in the base directory
subdirectories=$(find "$base_directory" -maxdepth 1 -mindepth 1 -type d)

# Loop through the immediate subdirectories and add them to PYTHONPATH
for dir in $subdirectories; do
    PYTHONPATH="$PYTHONPATH:$dir"
done

# Remove the leading colon if it exists
PYTHONPATH=$(echo $PYTHONPATH | sed 's/^://')

# Set the PYTHONPATH environment variable
export PYTHONPATH

# Optional: Display the updated PYTHONPATH
echo "Updated PYTHONPATH: $PYTHONPATH"


export PYTHONPATH=$(find "/Users/anushkrishnav/Documents/Projects/DevGPT" -maxdepth 1 -mindepth 1 -type d -exec printf "{}:" \; | sed 's/:$//')
