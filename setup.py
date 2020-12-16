import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LexData",
    version="0.2.0",
    author="Michael F. Schoenitzer",
    author_email="michael@schoenitzer.de",
    description="A tiny package for editing Lexemes on Wikidata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nudin/LexData",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests>=2.22.0"
    ],
)
