#!/bin/bash


echo "Running tests on shodan_service.py..."
# set ownership of file to shodan

pytest tests/test_shodan.py -v 
