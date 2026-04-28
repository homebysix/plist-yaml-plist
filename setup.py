#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from plistyamlplist_lib.version import __version__

VERSION = __version__

setup(
    name="plistyamlplist",
    version=VERSION,
    py_modules=["plistyamlplist"],
    packages=find_packages(include=["plistyamlplist_lib", "plistyamlplist_lib.*"]),
    install_requires=["ruamel.yaml<0.18.0"],
    entry_points={
        "console_scripts": [
            "plistyamlplist=plistyamlplist:main",
            "tidy-autopkg-recipes=plistyamlplist_lib.tidy_cli:main",
        ],
    },
)
