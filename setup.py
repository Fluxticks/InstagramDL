from setuptools import setup, find_packages

setup(
    name="instagram-dlpy",
    version="0.0.1",
    url="https://github.com/Fluxticks/InstagramDL",
    download_url="https://github.com/Fluxticks/InstagramDL/archive/v0.0.1.tar.gz",
    author="Fluxticks",
    packages=find_packages(),
    install_requires=["playwright",
                      "bs4",
                      "lxml"],
    description="A package to gather post information for a given Instagram post",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10"
    ],
    keywords=["instagram",
              "playwright",
              "async"],
)
