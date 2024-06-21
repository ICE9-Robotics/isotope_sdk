import sys
import subprocess

GITHUB_REPO = "https://github.com/ICE9-Robotics/isotope_sdk.git"


def get_cmd(branch, package):
    return f"git+{GITHUB_REPO}@{branch}#subdirectory={package}"


def main(branch=""):
    isotope = "python_lib/isotope"
    unit2 = "python_lib/unit2_controller"

    if branch == "":
        branch = "main"
        print("Install from main branch")
    else:
        print(f"Install from {branch} branch")

    subprocess.run(["pip", "install", get_cmd(branch, isotope)])
    subprocess.run(["pip", "install", get_cmd(branch, unit2)])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
    print("Installation complete.")
