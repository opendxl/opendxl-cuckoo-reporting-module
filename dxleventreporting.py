# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################
"""
DXL Event Reporting module for Cuckoo version 2.0.5.

Cuckoo report processing module which sends the Cuckoo analysis report data as a Data Exchange Layer (DXL) event on a
DXL Fabric. This module will send out the Cuckoo analysis report data in two DXL events. One event will contained
the analysis report in a compressed format and will be sent on the DXL topic "/cuckoo/event/report/zip". The second
event will contain the info and target sections of the Cuckoo analysis report and any sections specified in the
"items_to_include_in_report" setting under the "[dxleventreporting]" section of the report.conf file. The second event
will be sent on the topic "/cuckoo/event/report".

In order to make use of this module the user must install the OpenDXL Python Client, complete the OpenDXL Python Client
provisioning, and set the setting "dxl_client_config_file" with the location of the OpenDXL Python Client config
file under the "[dxleventreporting]" section in Cuckoo's report.conf file.

For more information on the OpenDXL Python Client please see https://github.com/opendxl/opendxl-client-python/wiki.
"""

import calendar
import datetime
import json
import logging
import re
import sys
import zlib

from cuckoo.common.abstracts import Report
from cuckoo.common.exceptions import CuckooReportError
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from dxlclient.message import Event

# Logger
log = logging.getLogger(__name__)

# Topics to publish DXL Events on
CUCKOO_ZIP_EVENT_TOPIC = "/cuckoo/event/report/zip"
CUCKOO_REPORT_EVENT_TOPIC = "/cuckoo/event/report"

# Analysis report keys
INFO_REPORT_KEY = "info"
TARGET_REPORT_KEY = "target"


def serialize_datetime_objects(obj):
    """
    Function to serialize datetime objects.

    :param obj: An object that cannot be serialized by default
    :return: A serialized datetime object.
    """
    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        return calendar.timegm(obj.timetuple()) + obj.microsecond / 1000000.0
    raise TypeError("%r is not JSON serializable" % obj)


def sub_level_getter(level, key):
    """
    Function used to get the value of a key that is multiple levels deep in a multi-level
    dictionary.

    :param level: Multi-level dictionary
    :param key: Key to find in the dictionary
    :return: The value associated with the key or the empty string
    """
    return "" if level is "" else level.get(key, "")


def create_and_get_sub_level(level, key):
    """
    Function used to create a sub level in a dictionary if it does not already exist and to return the value
    for sub level.

    :param level: Multi-level dictionary
    :param key: Key to add to the dictionary if it does not already exist
    :return: The value associated with the key in the multi-level dictionary
    """
    return level.setdefault(key, {})


class DXLEventReporting(Report):
    """
    Broadcast Cuckoo report information over McAfee Data Exchange Layer as a DXL event
    """

    def run(self, results):
        """
        Sends Cuckoo report as a DXL event on a DXL Fabric.

        @param results: Cuckoo results dict.
        @raise CuckooReportError: if fails to send Cuckoo report as a DXL event.
        """

        try:
            # Create DXL Client config
            dxl_client_config_file = self.options.get("dxl_client_config_file")

            if dxl_client_config_file is None:
                raise ValueError("Missing dxl_client_config_file setting under the "
                                 "[dxleventreporting] section in the report.conf file.")

            config = DxlClientConfig.create_dxl_config_from_file(dxl_client_config_file)

            # Diction of data to send out as the report on DXL
            report_dict = {}

            # Convert results to JSON string
            report_json_string = json.dumps(results, default=serialize_datetime_objects, indent=self.options.indent,
                                            encoding="UTF-8")

            # Compress the Cuckoo results
            zlib_obj = zlib.compressobj(-1, zlib.DEFLATED, 31)
            compressed_report_data = zlib_obj.compress(report_json_string) + zlib_obj.flush()

            # Initialize DXL client using our configuration
            log.info("Creating DXL Client")
            with DxlClient(config) as client:

                log.info("Connecting to Broker")
                client.connect()

                # Create the DXL Event for zipped data
                zipped_event = Event(CUCKOO_ZIP_EVENT_TOPIC)

                # Set the payload to be the compressed Cuckoo report analysis
                zipped_event.payload = compressed_report_data

                # Publish the full zipped reported if the payload size is smaller than one megabyte.
                if sys.getsizeof(zipped_event.payload) < 1000000:
                    log.info("Publishing full zipped report to DXL on topic %s", CUCKOO_ZIP_EVENT_TOPIC)
                    client.send_event(zipped_event)
                else:
                    log.info("Report too large. Not publishing zipped report to DXL.")

                # Add the info and target entries from the Cuckoo results
                report_dict[INFO_REPORT_KEY] = results.get(INFO_REPORT_KEY, {})
                report_dict[TARGET_REPORT_KEY] = results.get(TARGET_REPORT_KEY, {})

                # Add items listed from the "items_to_include_in_report" setting in the report.conf to the report
                items_to_include_in_report = self.options.get("items_to_include_in_report")
                if items_to_include_in_report is not None:
                    # Get rid of any white space characters in the items_to_include_in_report string
                    items_to_include_in_report = re.sub(r"\s+", "", items_to_include_in_report)

                    # Loop over list of items to include
                    for report_include_item in items_to_include_in_report.split(","):
                        # If the item does not have sub items then add it directly to the results report dictionary
                        if "." not in report_include_item:
                            report_dict.update({report_include_item: results.get(report_include_item, {})})
                            continue

                        # Process items to include that have sub items
                        sub_sections_list = report_include_item.split(".")
                        # Find the value in the Cuckoo results dictionary
                        sub_section_value = reduce(sub_level_getter, sub_sections_list, results)
                        # Create all of the sub item levels in the results reports dictionary
                        result_sub_section = reduce(create_and_get_sub_level, sub_sections_list[0:-1], report_dict)
                        # Add the value found in the Cuckoo results
                        result_sub_section.update({sub_sections_list[-1]: sub_section_value})

                # Create the DXL Event
                report_event = Event(CUCKOO_REPORT_EVENT_TOPIC)

                # Set event payload to be the JSON of the results report dictionary
                report_event.payload = json.dumps(report_dict, default=serialize_datetime_objects).encode("UTF-8")

                # Publish the Event to the DXL Fabric
                log.info("Publishing Cuckoo report to DXL on topic %s", CUCKOO_REPORT_EVENT_TOPIC)
                client.send_event(report_event)

        except Exception as ex:
            log.exception("Error sending Cuckoo report out as a DXL event.")
            raise CuckooReportError("Failed to send Cuckoo report as a DXL event: %s" % ex)
