"""
Setup configuration for Obesity ML Project
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="obesity-ml-project",
    version="1.0.0",
    author="ML Team 52",
    author_email="team52@example.com",
    description="Machine Learning project for obesity estimation with refactored code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/obesity-ml-project",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "mlflow>=2.8.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "pytest>=7.4.0",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "pylint>=2.17.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
