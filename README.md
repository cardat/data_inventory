CARDAT Data Inventory
================
2025-02-12

## About

The CARDAT Data Inventory is a Python **web2py** app to help manage
research metadata. Originally designed for ecological datasets (using
[Ecological Metadata Language](https://eml.ecoinformatics.org/)
concepts), it has been adapted more generally to suit datasets
pertaining to the CARDAT study focus areas, namely **air pollution,
climate change, energy and health**.

The inventory supports the [FAIR
principles](https://doi.org/10.1038/sdata.2016.18) with overarching tree
layout of projects and datasets, and structured metadata fields.
Additionally it allow recording of dataset requests and access.

The **web2py** app can run as simple standalone desktop app using an
SQLite database file or a PostgreSQL database server for shared and
concurrent access by a team.

## To install

1.  Download the [2.x version web2py
    binaries](http://www.web2py.com/init/default/download) and unzip
2.  Put all the files into your web2py/applications as
    `cardat_data_inventory` or the name you want
3.  Double-click to run the web2py.exe file and go to
    `127.0.0.1:8000/cardat_data_inventory` in your browser
4.  In the top right corner, sign up with a local username and password

## General database structure

### Dataset metadata

The inventory uses a hierarchical structure project-dataset-entity,
where `project` is a large overarching program/project containing one or
more `dataset`s. Each dataset has a defined study focus, temporal and
spatial range. For a dataset, one or more `entity`(ies) may be
described, each representing (typically) a file. An `entity` can have
attributes (`attr`, variable descriptions) attached.

    ├── keyword
    ├── personnel
    ├── project
    │   ├── j_project_personnel       -> to personnel
    │   ├── dataset
    │   │   ├── intellectualright
    │   │   ├── dataset_publication
    │   │   ├── entity
    │   │   │   ├── attr
    │   │   ├── j_dataset_keyword     -> to keyword
    │   │   ├── j_dataset_personnel   -> to personnel
    │   │   ├── j_request_dataset     -> to accessrequest
    │   │   ├── dataset_linkage       -> to self-referential dataset

The `dataset` level is the centre of the inventory structure. Further
tables are attached to each `dataset` to describe the:

- licensing (`intellectualright`),
- related publications describing methodology (`dataset_publication`)
- keywords (`keyword` and joining table `j_dataset_keyword`)
- personnel (`personnel` and joining_table `j_dataset_personnel`)

Note that `personnel` can also be attached to a project through
`j_project_personnel`.

Dataset relationships are expressed by the table `dataset_linkage` -
this may include inputs/derivations and subsets/extractions.

### Access requests

Requests to access the datasets described above are recorded in a
separate set of tables, central of which are the `cardat_user` and
`accessrequest` tables. All user details are input to `cardat_user`
(such as name, contact details, affiliations, ORCID). A single
`accessrequest` record describes a request for one or more datasets for
a specified project/purpose.

An `accessrequest` is linked to requested `dataset`s through
`j_request_dataset` with fields to record date of request approval, and
linked to `cardat_user` through `accessor` (with begin and end date of
access). Thus one user may have multiple requests (for different
purposes and different sets of requested datasets), and one request may
have multiple users involved.

Additionally, any outcomes (e.g. journal paper, report, thesis, press
article) from an `accessrequest` can be put into a linked
`request_outcome` for reporting purposes.

    ├── cardat_user
    ├── accessrequest
    │   ├── request_output
    │   ├── accessor            -> to cardat_user
    │   ├── j_request_dataset   -> to dataset

## Roadmap for Python 3

1.  Investigate port to py4web (successor to web2py - [GitHub
    link](https://github.com/web2py/py4web))
2.  If using the Postgres database backend need to use older psycopg2
    (to avoid postgres
    `RuntimeError: No driver of supported ones ('psycopg2',) is available`)

<!-- -->

    sudo apt update
    curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
    sudo python2 get-pip.py
    pip2 install psycopg2-binary

Licence: CC-BY-4.0

![](cc-by-4_0.png)
