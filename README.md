# fmfexporter

FMF (Flexible Metadata Format) test case exporter tool.

This tool can be used to convert and export Test Cases defined
using an [FMF](https://fmf.readthedocs.io/en/latest/) tree.

The test cases must be defined according to an internal schema (*WIP* - will be shared here)
and the fmfexporter can parse them and invoke a selected adapter to convert / export the
select test cases into an external ALM related tool.

Format for defining the test case is YAML (Simple example available -- *WIP* -- in the test directory). 

## Pre-requisites

* python 3.6+
* recommended to install fmfexporter or its requirements in a virtualenv

## Usage

For basic usage information, use:

```
fmfexporter --help
```

## Adapters

This tool provides a generic `fmfexporter.fmf_adapter.FMFAdapter` interface that can be implemented
for new external ALM related tools.

### Polarion ALM

Adapter (early stage) that can export a test case defined using FMF (compliant with internal FMF Test Case metadata
schema) into Polarion test case importer API.

For help, use:

```
fmfexporter polarion --help
```

## Contributors

* Fernando Giorgetti <fgiorget@redhat.com>
* Dominik Lenoch <dlenoch@redhat.com>

## Acknowledgments

* [fmf](https://fmf.readthedocs.io/en/latest/) - Flexible Metadata Format - Makes it easier to document
and query for your metadata.
