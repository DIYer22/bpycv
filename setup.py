#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
import os

package_name = "bpycv"
here = os.path.dirname(os.path.realpath(__file__))

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f]

with open("README.md", encoding='utf-8') as f:
    long_description = f.read()

info = {}
with open(os.path.join(here, package_name, "__info__.py")) as f:
    exec(f.read(), info)


setuptools.setup(
    name=package_name,
    version=info["__version__"],
    author=info["__author__"],
    author_email=info["__author_email__"],
    description=info["__description__"],
    long_description=info["__description__"],
    long_description_content_type="text/markdown",
    url=info["__url__"],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=requirements,
    classifiers=info["__classifiers__"],
)
