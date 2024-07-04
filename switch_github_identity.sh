#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <identity>"
    echo "Available identities: giladnah_github, hailocs, default"
    exit 1
fi

IDENTITY=$1
CONFIG_FILE=~/.ssh/config

case $IDENTITY in
    giladnah_github)
        # Comment out all IdentityFile lines under Host github.com
        sed -i '/^Host github.com$/,/^Host / s|^\( *IdentityFile ~/.ssh/id_rsa_giladnah_github\)|#\1|' $CONFIG_FILE
        sed -i '/^Host github.com$/,/^Host / s|^\( *IdentityFile ~/.ssh/id_rsa_hailocs\)|#\1|' $CONFIG_FILE
        sed -i '/^Host github.com$/,/^Host / s|^\( *IdentityFile ~/.ssh/id_rsa\)|#\1|' $CONFIG_FILE

        # Uncomment the relevant IdentityFile line
        sed -i '/^Host github.com$/,/^Host / s|^#\( *IdentityFile ~/.ssh/id_rsa_giladnah_github\)|\1|' $CONFIG_FILE
        ;;
    hailocs)
        # Comment out all IdentityFile lines under Host github.com
        sed -i '/^Host github.com$/,/^Host / s|^\( *IdentityFile ~/.ssh/id_rsa_giladnah_github\)|#\1|' $CONFIG_FILE
        sed -i '/^Host github.com$/,/^Host / s|^\( *IdentityFile ~/.ssh/id_rsa_hailocs\)|#\1|' $CONFIG_FILE
        sed -i '/^Host github.com$/,/^Host / s|^\( *IdentityFile ~/.ssh/id_rsa\)|#\1|' $CONFIG_FILE

        # Uncomment the relevant IdentityFile line
        sed -i '/^Host github.com$/,/^Host / s|^#\( *IdentityFile ~/.ssh/id_rsa_hailocs\)|\1|' $CONFIG_FILE
        ;;
    default)
        # Comment out all IdentityFile lines under Host github.com
        sed -i '/^Host github.com$/,/^Host / s|^\( *IdentityFile ~/.ssh/id_rsa_giladnah_github\)|#\1|' $CONFIG_FILE
        sed -i '/^Host github.com$/,/^Host / s|^\( *IdentityFile ~/.ssh/id_rsa_hailocs\)|#\1|' $CONFIG_FILE
        sed -i '/^Host github.com$/,/^Host / s|^\( *IdentityFile ~/.ssh/id_rsa\)|#\1|' $CONFIG_FILE

        # Uncomment the relevant IdentityFile line
        sed -i '/^Host github.com$/,/^Host / s|^#\( *IdentityFile ~/.ssh/id_rsa\)|\1|' $CONFIG_FILE
        ;;
    *)
        echo "Unknown identity: $IDENTITY"
        exit 1
        ;;
esac

echo "Switched GitHub identity to: $IDENTITY"
