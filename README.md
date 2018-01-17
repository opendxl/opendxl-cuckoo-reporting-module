# OpenDXL Cuckoo Reporting Module
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

Cuckoo reporting module for version 2.0.5

## Documentation

See the
[Wiki](https://github.com/opendxl/opendxl-cuckoo-reporting-module/wiki)
for an overview, installation instructions, and examples of the OpenDXL Cuckoo Reporting Module.

## Installation

To start using the OpenDXL Cuckoo Reporting Module:

* Download the
  [Latest Release](https://github.com/opendxl/opendxl-cuckoo-reporting-module/releases/latest)
* Extract the release .zip file
* Copy `dxleventreporting.py` into the `cuckoo/modules/reporting/` directory where you have installed Cuckoo.
* Update `reporting.conf` in the `cuckoo/conf` directory to have a `[dxleventreporting]` section similar to the
example below.
* Install the OpenDXL Python Client with the command `pip install dxlclient`
* Create a directory that will contain the OpenDXL Python Client configuration files created when provisioning the client.
* In the directory created in step four complete the OpenDXL Python Client provisioning
process - https://opendxl.github.io/opendxl-client-python/pydoc/provisioningoverview.html.
* Update the `dxl_client_config_file` setting under the `[dxleventreporting]` section in the `reporting.conf` in
the `cuckoo/conf` directory to have the path to the `dxlclient.config` created in step five.
* Update the `items_to_include_in_report` setting under the `[dxleventreporting]` section in
the `reporting.conf` in the `cuckoo/conf` directory to have any additional fields from the Cuckoo report you
wish to broadcast over DXL.

`reporting.conf` example `[dxleventreporting]` section:
```
[dxleventreporting]
enabled = yes
dxl_client_config_file = /home/cuckoo/opendxl/dxlclient.config
items_to_include_in_report =
send_compressed_event = no
compressed_event_max_size = 512000
```

## Usage

* Use an OpenDXL Python Client, OpenDXL Console, or OpenDXL Environment (https://github.com/opendxl) to subscribe to
the topic `/cuckoo/event/report` in order to receive the Cuckoo report analysis.
* Modify the `items_to_include_in_report` to include a comma separated list of any items from the Cuckoo analysis you
would like to include in the report sent over DXL. By default the `info` and `target` sections of the Cuckoo
analysis are included.
* Run Cuckoo as normal
* Once Cuckoo completes analysis the report analysis will be sent out as a DXL Event on the
topic `/cuckoo/event/report`
* If you do not receive the event with your DXL Client that is subscribed to the topic `/cuckoo/event/report` after
Cuckoo finishes its analysis then please see the Cuckoo logs for issues.

Note, if you wish to receive the full compressed Cuckoo report analysis over DXL then you will need do the following:
* Enable the `send_compressed_event` setting under the `[dxleventreporting]` section of Cuckoo's reporting.conf file.
* The default size limit for the compressed Cuckoo analysis report is 500KB. Cuckoo analysis reports larger in size
than this will not be sent. If you wish to increase the size limit for the compressed Cuckoo analysis report then
you will need to modify the `compressed_event_max_size` setting under the `[dxleventreporting]` section of
Cuckoo's reporting.conf file. Please note that DXL Brokers will not process DXL messages larger than
one megabyte in size.
* Use an OpenDXL Client to subscribe to the topic `/cuckoo/event/report/zipped` .
* The OpenDXL Client must decompress the payload when a message is received on the topic `/cuckoo/event/report/zipped`.


## Bugs and Feedback

For bugs, questions and discussions please use the
[GitHub Issues](https://github.com/opendxl/opendxl-cuckoo-reporting-module/issues).

## LICENSE

Copyright 2017 McAfee, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
