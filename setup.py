# encoding:utf-8
import setuptools
from os import environ
import rshell as application
from importlib import reload

try:
    tag = environ["CI_COMMIT_TAG"]
except KeyError:
    raise KeyError("No version is given. See $CI_COMMIT_TAG in gitlab pipeline.")

with open(f"{application.__name__}/__init_.py", "r", encoding="utf-8") as file:
    content = file.read()

content.replace(f"__version__ = {repr(application.__version__)}", f"__version__ = {tag}")

with open(f"{application.__name__}/__init_.py", "w", encoding="utf-8") as file:
    content = file.write(content)

reload(application)
assert application.__version__


def requirements():
    with open("requirements.txt", "r", encoding="utf-8") as file:
        return [ele.strip('\n') for ele in file.readlines()]



setuptools.setup(
    name="setuplaunchertest",
    version=application.__version__,
    author="Julien Vince",
    author_email="julien.vince@gmail.com",
    description="Librairie d'exécution de commandes shell pour robotframework.",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements(),
    python_requires='>=3.6',
)
