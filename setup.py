import setuptools
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PyBASS3",
    version="0.0.1",
    author="DevDave",
    author_email="devdave@ominian.net",
    description="A Python 3 compatible, managed, wrapper around the c BASS Audio library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devdave/pybass3",
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Topic :: Multimedia :: Sound/Audio",


    ],
    packages=find_packages("pybass3"),
    package_dir={"": "pybass3"},
    package_data={
        "": ["vendor/*.dll", "vendor/*.h", "vendor/*.txt"],
    },
    python_requires = ">= 3.6"

)