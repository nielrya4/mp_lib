#!/usr/bin/env python3
"""
Setup script for mp_lib - Microplastics Analysis Library
"""
from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Microplastics Analysis Library with CLI tools"

# Read requirements
def read_requirements():
    requirements = [
        'numpy>=1.20.0',
        'scipy>=1.7.0',
        'matplotlib>=3.4.0',
        'pandas>=1.3.0',
        'openpyxl>=3.0.0',
        'scikit-learn>=1.0.0'
    ]
    return requirements

setup(
    name="mp_lib",
    version="1.0.0",
    author="Ryan Nielsen",
    author_email="nielrya4@isu.edu",
    description="Microplastics Analysis Library with CLI tools",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/nielrya4/mp_lib",
    packages=find_packages(),
    py_modules=['mp_cli'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Geology",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'mp-cli=mp_cli:main',
            'mp_cli=mp_cli:main',
            'microplastics=mp_cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="microplastics analysis chemistry environment pollution",
    project_urls={
        "Bug Reports": "https://github.com/nielrya4/mp_lib/issues",
        "Source": "https://github.com/nielrya4/mp_lib",
        "Documentation": "https://github.com/nielrya4/mp_lib/wiki",
    },
)