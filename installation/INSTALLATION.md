# Installation scripts

## From local source

You can use either "install.sh" or "install.py" to install the Python Library from local source, which you have downloaded with this script.

"install.sh" is a bash script which requires additional software in Windows OS. If you are using linux or macos, simply open a terminal, `cd` to this installation directory and type:
```
./install.sh
```

"install.py" is a python script which can run in Windows terminal or powershell. You can right click on the empty space in the installation folder, select "Open In Terminal" (or start a terminal and `cd` to the installation directory) and type:
```
python3 install.py
```

In either case, you should see the terminal prompt saying:
```
...
Successfully installed isotope
...
Successfully installed unit2_controller
Installation complete.
```

## From Github repository

You may also use "install_from_github.sh" or "install_from_github.py" to install from online source. This is useful when you want to update the package to the newest version or from the `dev` branch while your local source is outdated. 
