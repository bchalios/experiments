import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
        name="experiment",
        version="0.0.1",
        description="A Python package for running experiments on BSC machines",
        author="Babis Chalios",
        author_email="babis.chalios@bsc.es",
        long_description=long_description,
        long_description_content_type="test/markdown",
        url="git@github.com:bchalios/experiments.git",
        packages=["experiment"],
        license='GPL3'
)
