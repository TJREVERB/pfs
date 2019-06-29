import os
from invoke import task


@task
def run(c, production=False, debug=False):
    if production:
        c.run("python3 main.py")
    else:
        if debug:
            c.run("pipenv run python3 main.py -d")
        else:
            c.run("pipenv run python3 main.py")


@task
def reformat(c):
    c.run("pipenv run autopep8 --in-place -r ./")


@task
def deploy(c):
    # Lock the requirements in a file
    c.run("pipenv lock -r > requirements.txt")

    with open("requirements.txt", "r") as file_locked:
        requirements = file_locked.readlines()
    file_locked.close()
    os.remove("requirements.txt")

    # It's much quicker to use the Debian packages to install these vs. apt
    requirements_skip = ["astropy", "numpy", "scipy"]
    requirements_skip_to_install = []

    # Remove the unwanted packages in requirements.txt, add their package names to list
    with open("requirements.txt", "w") as file_new:
        for pos, line in enumerate(requirements):
            write_line = True
            for r in requirements_skip:
                if r in line:
                    requirements_skip_to_install.append("python3-" + r)
                    write_line = False

            if write_line:
                file_new.write(line)

    file_new.close()

    # Install skipped packages using apt
    for r in requirements_skip_to_install:
        c.run("sudo apt install -y " + r)

    # Install requirements.txt using pip
    c.run("sudo pip3 install --verbose -r requirements.txt")
    os.remove("requirements.txt")
