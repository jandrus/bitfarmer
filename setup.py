#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="bitfarmer",
    version="0.1.1",
    author="jimboslice",
    author_email="jandrus@citadel.edu",
    description="ASIC manager.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jandrus/bitfarmer.git",
    packages=find_packages(where="bitfarmer"),
    package_dir={"": "bitfarmer"},
    install_requires=[
        "requests>=2.20",
        "colorama>=0.4.6",
        "ntplib>=0.4.0",
        "platformdirs>=4.3.6",
        "yaspin>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "bitfarmer=bitfarmer.bitfarmer:main",
        ],
    },
)
