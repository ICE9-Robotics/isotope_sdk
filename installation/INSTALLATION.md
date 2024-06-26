# Installation scripts

## From local source

You can use "install.sh" or "install.py" to install the Python Library from the local source, which you downloaded with this script.

"install.sh" is a bash script which requires additional software in Windows OS. If you are using Linux or macOS, open a terminal, `cd` to this installation directory and type:
```
./install.sh
```

"install.py" is a Python script which can run in a Windows terminal or Powershell. You can right click on the empty space in the installation folder, select "Open In Terminal" (or start a terminal and `cd` to the installation directory) and type:
```
python3 install.py
```

Using either script, you should see the terminal prompt saying:
```
...
Successfully installed isotope
...
Successfully installed unit2_controller
Installation complete.
```

## From Github repository

"install_from_github.sh" or "install_from_github.py" can be used to install the packages from online sources. This is useful when you want to update the package to the newest version or from a branch while your local source is outdated. 

The use of the scripts is similar to the above:
```
python3 install_from_github.py
./install_from_github.sh
```
The above commands install the packages from the main branch, and you may pass an argument indicating which branch, tag or commit you would like to install from. For example, to install from the `dev` branch:

```
python3 install_from_github.py dev
./install_from_github.sh dev
```

or from the `caa35e0fe3ad2d3be26af10f2222420bda695bf8` commit:
```
python3 install_from_github.py caa35e0fe3ad2d3be26af10f2222420bda695bf8
./install_from_github.sh caa35e0fe3ad2d3be26af10f2222420bda695bf8
```
