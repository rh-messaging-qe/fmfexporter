import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

files = ["metadata/*", "metadata/*/*", "metadata/.*/*"]

setuptools.setup(
    name='fmfexporter',
    version='0.1',
    scripts=['bin/fmfexporter'],
    python_requires='>=3.6',
    install_requires=['fmf', 'requests', 'jira', 'urllib3'],
    setup_requires=['pytest-runner', 'fmf', 'requests', 'urllib3'],
    tests_require=['pytest'],
    author="Fernando Giorgetti, Dominik Lenoch",
    author_email="fgiorget@redhat.com, dlenoch@redhat.com",
    license="Apache-2.0",
    description="Flexible Metadata Format test-case exporter tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rhmessagingqe/fmfexporter",
    packages=setuptools.find_packages(),
    package_data={'fmfexporter': files},
    provides=['fmfexporter'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
