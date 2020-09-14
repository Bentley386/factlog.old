import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="exploratory_analysis_FACTLOG-klemenkenda", # Replace with your own project and username
    version="0.0.1",
    author="Klemen Kenda",
    author_email="klemen.kenda@ijs.si",
    description="Exploratory analysis for FACTLOG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JozefStefanInstitute/factlog",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)