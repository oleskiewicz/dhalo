#!/usr/bin/env python
from os import path

from setuptools import find_packages, setup

with open(path.join(path.abspath(path.dirname(__file__)), "README.rst")) as f:
    long_description = f.read()

setup(
    name="dhalo",
    version="0.1",
    author="Piotr Oleskiewicz",
    author_email="piotr.oleskiewicz@durham.ac.uk",
    description=(
        "A set of tools for reading and analysing halo catalogues in DHalo format"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3",
    keywords="dhalo cosmology astrophysics dark_matter halo_finder",
    url="https://gitlab.com/oleskiewicz/dhalo",
    packages=find_packages(exclude=["data", "src", "out"]),
    install_requires=["defopt", "h5py", "numpy", "pandas"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Intended Audience :: Science/Research"
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
