import setuptools
import sys

if sys.version_info < (3, 6):
    sys.exit('Python < 3.6 is not supported')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='fmfexporter',
    version='0.1',
    scripts=['bin/fmfexporter'],
    install_requires=['fmf', 'requests', 'urllib3==1.24.1'],
    setup_requires=['pytest-runner', 'fmf', 'requests', 'urllib3==1.24.1'],
    tests_require=['pytest'],
    author="Fernando Giorgetti, Dominik Lenoch",
    author_email="fgiorget@redhatcom, dlenoch@redhat.com",
    license="Apache-2.0",
    description="Flexible Metadata Format test-case exporter tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rhmessagingqe/fmfexporter",
    packages=setuptools.find_packages(),
    provides=['fmfexporter'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
