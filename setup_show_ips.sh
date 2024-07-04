#!/bin/bash

# Create the show_ips.sh script
cat << 'EOF' > /home/$USER/show_ips.sh
#!/bin/bash

# Open a new terminal window and print the IP addresses
lxterminal -e "bash -c 'echo \"IPv4 addresses:\"; hostname -I; echo \"IPv6 addresses:\"; ip -6 addr | grep inet6 | awk '\''{print \$2}'\'' | cut -d/ -f1; exec bash'"
EOF

# Make the script executable
chmod +x /home/$USER/show_ips.sh

# Add the script to crontab for startup
(crontab -l ; echo "@reboot /home/$USER/show_ips.sh") | crontab -

echo "Setup complete. The IP display script will run at startup."
