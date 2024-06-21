#!/bin/bash
branch=$1
if [ "$branch" = "" ]; then
    echo "Install from main branch"
    branch="main"
else
    echo "Install from $1 branch"
fi

python3 -m pip install git+https://github.com/ICE9-Robotics/isotope_sdk.git@$branch#subdirectory=python_lib/isotope
python3 -m pip install git+https://github.com/ICE9-Robotics/isotope_sdk.git@$branch#subdirectory=python_lib/unit2_controller

echo "Installation completed"