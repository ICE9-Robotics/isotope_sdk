cd $(dirname $0)/..

pdoc --html --output-dir docs/ --force python_lib/isotope/isotope --template-dir docs/templates/
pdoc --html --output-dir docs/ --force python_lib/unit2_controller/unit2_controller --template-dir docs/templates/