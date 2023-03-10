.. SPDX-FileCopyrightText: 2008-2023 Luis Falcón 
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

gnuhealth_product_uploader.py

Simple script to show ways to interface with GNU Health in a
non-interactive way.
This program reads a CSV formatted file with that contains the products

Included in this directory a sample product_sample.csv, that contains 
some products (services)


Requirements :
This version works with the following versions :

- GNU Health : 3.6
- Proteus library : 5.0 

Installing proteus :
$ pip install --upgrade --user "proteus>=5.0,<5.1" 


Usage :
Invoke the program and pass the csv formatted file as an argument
eg:

$ python3 ./gnuhealth_product_uploader.py products_sample.csv

The main steps are :
- Test connection to the GNU Health server
- Check the csv file
- Upload the results.


This is part of GNU Health, the Free Hospital and Health Information System
https://www.gnuhealth.org
