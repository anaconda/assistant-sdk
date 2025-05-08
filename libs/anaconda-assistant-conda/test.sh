#!/bin/zsh

# Run the conda install command
script -q -e "conda create -n myenv --dry-run anaconda-cloud-auth=0.7 pydantic=1" /dev/null