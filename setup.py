# coding=utf-8
from setuptools import find_packages, setup

setup(
    name="twitchdrives",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    package_data={
        "": ["*.json"],
    },
)
