import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyparallelize",
    version="0.1.0",
    author="Ismail Uddin",
    description="Package to simplify process of parallelising tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='GNU',
    url="https://github.com/ismailuddin/parallelize",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
