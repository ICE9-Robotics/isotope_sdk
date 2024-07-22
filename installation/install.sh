#!/bin/bash

cd $(dirname $0)/..

isotope_path=python_lib/isotope
unit2_path=python_lib/unit2_controller

# Remove existing build folders
if [ -d ${isotope_path}/build ]; then
    rm -rf ${isotope_path}/build
fi

if [ -d ${unit2_path}/build ]; then
    rm -rf ${unit2_path}/build
fi

# Install the packages
if [ "$1" = "debug" ]; then
    echo "Debug mode"
    python3 -m pip install -e ${isotope_path}
    python3 -m pip install -e ${unit2_path}
else
    echo "Release mode"
    python3 -m pip install ${isotope_path} --upgrade
    python3 -m pip install ${unit2_path} --upgrade
fi

echo "Installation completed"
