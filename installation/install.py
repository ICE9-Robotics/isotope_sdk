import os
import sys
import subprocess


def main(debug=False):
    root_dir = os.path.dirname(os.path.dirname(__file__))
    isotope = os.path.join(root_dir, "python_lib", "isotope")
    unit2 = os.path.join(root_dir, "python_lib", "unit2_controller")

    # remove build folders
    build_dir = os.path.join(isotope, "build")
    if os.path.exists(build_dir):
        print("Removing build folder under isotope")
        subprocess.run(["rm", "-rf", build_dir])
    build_dir = os.path.join(unit2, "build")
    if os.path.exists(build_dir):
        print("Removing build folder under unit2")
        subprocess.run(["rm", "-rf", build_dir])

    # install the packages
    if debug:
        print("Debug mode")
        subprocess.run(["pip", "install", "-e", isotope])
        subprocess.run(["pip", "install", "-e", unit2])
        return
    print("Release mode")
    subprocess.run(["pip", "install", isotope])
    subprocess.run(["pip", "install", unit2])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1] == "debug")
    else:
        main()
    print("Installation complete.")
