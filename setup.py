import setuptools
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PyBASS3",
    package_data={
        "pybass3": ["vendor/*.dll", "vendor/*.h", "vendor/*.txt", "vendor/*.so"],
    },
    python_requires = ">= 3.6"

)