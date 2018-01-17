# OpenDXL Event Reporting Cuckoo Reporting Module

Cuckoo reporting module for version 2.0.5

Requirements
------
* Cuckoo Sandbox 2.0.5 or greater (https://cuckoosandbox.org/)
* OpenDXL Python Client (https://github.com/opendxl/opendxl-client-python) which can be obtained from PyPI

Installation
------

1. Copy `dxleventreporting.py` into the `cuckoo/modules/reporting/` directory where you have installed Cuckoo.
2. Update `reporting.conf` in the `cuckoo/conf` directory to have a `[dxleventreporting]` section similar to the example below.
3. Install the OpenDXL Python Client with the command `pip install dxlclient`
4. Create a directory that will contain the OpenDXL Python Client configuration files created when provisioning the client.
5. In the directory created in step four complete the OpenDXL Python Client provisioning process - https://opendxl.github.io/opendxl-client-python/pydoc/provisioningoverview.html.
6. Update the `dxl_client_config_file` setting under the `[dxleventreporting]` section in the `reporting.conf` in the `cuckoo/conf` directory to have the path to the `dxlclient.config` created in step five.
7. Update the `items_to_include_in_report` setting under the `[dxleventreporting]` section in the `reporting.conf` in the `cuckoo/conf` directory to have any additional fields from the Cuckoo report you wish to broadcast over DXL.

`reporting.conf` example `[dxleventreporting]` section:
```
[dxleventreporting]
enabled = yes
dxl_client_config_file = /home/cuckoo/opendxl/dxlclient.config
items_to_include_in_report =
```

Usage
------

1. Use an OpenDXL Python Client, OpenDXL Console, or OpenDXL Environment (https://github.com/opendxl) to subscribe to the topic `/cuckoo/event/report` in order to receive the Cuckoo report analysis.
2. Modify the `items_to_include_in_report` to include a comma separated list of any items from the Cuckoo analysis you would like to include in the report sent over DXL. By default the `info` and `target` sections of the Cuckoo analysis are included.
3. Run Cuckoo as normal
4. Once Cuckoo completes analysis the report analysis will be sent out as a DXL Event on the topic `/cuckoo/event/report`
5. If you do not receive the event with your DXL Client that is subscribed to the topic `/cuckoo/event/report` after Cuckoo finishes its analysis then please see the Cuckoo logs for issues.

Note, if you wish to receive the full compressed Cuckoo report analysis over DXL then you will need to subscribe to the topic `/cuckoo/event/report/zipped` and decompress the payload when a message is received.
If the compressed Cuckoo analysis report is greater than one megabyte in size then it will not be sent over DXL.