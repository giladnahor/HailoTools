#!/bin/bash
# Run this script to create symbolic links to all bash and python scripts in the current directory
# with a prefix "gilad_" in the /usr/bin directory. The script will prompt the user for confirmation
# before creating the symbolic link.

# Define the target directory
TARGET_DIR="/usr/bin"

# Define a global variable to accept all
ACCEPT_ALL=false

# Function to create a symbolic link
link_script() {
    local script=$1
    local target=$2

    # Define the new name with prefix
    local new_name="gilad_$script"

    # Check if the target already exists
    if [ -L "$target/$new_name" ] || [ -e "$target/$new_name" ]; then
        echo "Link or file $new_name already exists. Skipping."
    else
        if $ACCEPT_ALL ; then
            echo "Automatically linking $script to $target/$new_name."
        else
            # Ask user for confirmation
            read -p "Do you want to link $script to $target/$new_name? (y/n/a for all): " -n 1 -r
            echo    # move to a new line
            if [[ $REPLY =~ ^[Aa]$ ]]
            then
                ACCEPT_ALL=true
                echo "Automatically linking $script to $target/$new_name."
            elif [[ $REPLY =~ ^[Yy]$ ]]
            then
                # Create the symbolic link
                ln -s "$(pwd)/$script" "$target/$new_name"
                echo "Linked $script to $target/$new_name."
            else
                echo "Skipping $script."
            fi
        fi
        if $ACCEPT_ALL ; then
            ln -s "$(pwd)/$script" "$target/$new_name"
        fi
    fi
}

# Iterate over each file in the current directory
for file in *; do
    # Check if the file is a bash or python script and is executable
    if [[ -f $file && -x $file && ($file == *.sh || $file == *.py) ]]; then
        link_script "$file" "$TARGET_DIR"
    fi
done

echo "Linking complete."