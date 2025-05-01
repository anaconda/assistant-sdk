#!/bin/bash

echo "\nRun this to deactivate:\n\nsource deactivate-demo.sh\n"

PROMPT='%# '
# Don't show env var in prompt
export CONDA_CHANGEPS1=false
# Alias so we can demo with `conda assist` 
alias conda=./env/bin/conda