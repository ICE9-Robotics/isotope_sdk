#!/bin/bash

cd $(dirname $0)/..

isotope_path=python_lib/isotope
unit2_path=python_lib/unit2_controller

if [ "$1" = "debug" ]; then
    echo "Debug mode"
    python -m pip install -e ${isotope_path}
    python -m pip install -e ${unit2_path}
else
    echo "Release mode"
    python -m pip install ${isotope_path}
    python -m pip install ${unit2_path}
fi

echo "Installation completed"
