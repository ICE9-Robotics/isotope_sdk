#!/bin/bash

cd $(dirname $0)/..

isotope_path=python_lib/isotope
unit2_path=python_lib/unit2_controller

if [ "$1" = "debug" ]; then
    echo "Debug mode"
    python3 -m pip install -e ${isotope_path}
    python3 -m pip install -e ${unit2_path}
else
    echo "Release mode"
    python3 -m pip install ${isotope_path}
    python3 -m pip install ${unit2_path}
fi

echo "Installation completed"
