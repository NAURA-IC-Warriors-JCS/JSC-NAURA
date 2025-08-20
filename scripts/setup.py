#!/usr/bin/env python3
"""
DRL-d: Deep Reinforcement Learning for Semiconductor Manufacturing
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="drl-d",
    version="1.0.0",
    author="DRL-d Team",
    author_email="your.email@example.com",
    description="Deep Reinforcement Learning for Semiconductor Manufacturing Scheduling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/DRL-d",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "web": [
            "flask>=2.0",
            "flask-cors>=3.0",
        ],
        "viz": [
            "matplotlib>=3.5",
            "seaborn>=0.11",
            "plotly>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "drl-d-train=src.main:main",
            "drl-d-analyze=scripts.analyze_training:main",
            "drl-d-viz=examples.rl_visualization_tool:main",
        ],
    },
)