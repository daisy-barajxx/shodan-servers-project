#!/bin/bash

# run the project
echo "Running the shodan apache service..."
# set ownership of the file to user
sudo chown daisy: /tmp/shodan_servers.out

# start the service 
python3 /usr/local/bin/shodan_service.py 
# or sudo systemctl start shodan.service
