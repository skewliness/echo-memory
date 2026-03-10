from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="echo-memory",
    version="2.0.0",
    author="Echo Memory Contributors",
    author_email="echo@github.com",
    description="A brain-like memory management system with temperature decay and association networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skewliness/echo-memory",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "lancedb>=0.5.0",
        "pyarrow>=14.0.0",
        "sentence-transformers>=2.2.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "echo=echo.cli:main",
        ],
    },
)
