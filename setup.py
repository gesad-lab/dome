import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="text2system",                     # This is the name of the package
    version="0.0.8",                        # The initial release version
    author="Anderson Martins Gomes",                     # Full name of the author
    author_email='andersonmg@gmail.com',
    url='https://github.com/andersonmgomes/text2system',
    description="A self-adaptative architecture implementation.",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    package_dir={'':'src'},     # Directory of the source code of the package
    packages=["text2system"],
)