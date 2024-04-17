from setuptools import setup, find_packages

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="instagram-dlpy",
    version="1.2.0",
    url="https://github.com/Fluxticks/InstagramDL",
    download_url="https://github.com/Fluxticks/InstagramDL/archive/v1.2.0.tar.gz",
    author="Fluxticks",
    packages=find_packages(),
    install_requires=["requests"],
    extras_require={
        ':python_version < "3.11"': [
            "StrEnum",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="A python package to download Instagram posts by URL without needing to login",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=["instagram", "api"],
)
