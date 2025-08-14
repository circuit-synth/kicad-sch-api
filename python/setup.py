"""
kicad-sch-api: Professional KiCAD Schematic Manipulation Library
A modern, high-performance Python library for programmatic manipulation of KiCAD schematic files
with exact format preservation and AI agent integration.
"""

from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_readme():
    with open(os.path.join(os.path.dirname(__file__), '..', 'README.md'), 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="kicad-sch-api",
    version="1.0.0",
    author="Circuit-Synth",
    author_email="info@circuit-synth.com",
    description="Professional KiCAD schematic manipulation library with exact format preservation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/circuit-synth/kicad-sch-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research", 
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "sexpdata>=0.0.3",
        "uuid",
        "pathlib",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "mcp": ["mcp>=0.1.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kicad-sch-api=kicad_sch_api.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/circuit-synth/kicad-sch-api/issues",
        "Source": "https://github.com/circuit-synth/kicad-sch-api",
        "Documentation": "https://circuit-synth.github.io/kicad-sch-api/",
    },
)