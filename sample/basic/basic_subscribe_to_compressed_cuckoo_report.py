# This sample demonstrates how to register a callback to receive Event messages
# from the DXL fabric for the compressed Cuckoo report analysis. Once the callback is registered, the sample
# waits to receive the compressed Cuckoo report analyses. In order for the OpenDXL Cuckoo Reporting Module
# to broadcast the compressed Cuckoo report analyses, the "send_compressed_event" setting under the
# "[dxleventreporting]" section of Cuckoo's reporting.conf file must be enabled.
import json
import logging
import os
import sys
import time
import zlib

from dxlclient.callbacks import EventCallback
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig

# Import common logging and configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# The compressed Cuckoo report Event topic
EVENT_TOPIC = "/cuckoo/event/report/zip"

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

# Create the client
with DxlClient(config) as client:

    # Connect to the fabric
    client.connect()

    # Create and add event listener
    class CuckooCompressedReportEventCallback(EventCallback):
        def on_event(self, event):
            # decompress zipped Cuckoo report
            decompressed_event_payload = zlib.decompress(event.payload, 31)

            # Print the payload for the received event
            print("Cuckoo compressed report received: ")

            decompressed_event_dict = json.loads(decompressed_event_payload.decode(encoding="UTF-8"))
            print json.dumps(decompressed_event_dict, sort_keys=True, indent=4, separators=(',', ': ')) + "\n"

    # Register the callback with the client
    client.add_event_callback(EVENT_TOPIC, CuckooCompressedReportEventCallback())

    # Wait until all events have been received
    print "Waiting for Cuckoo compressed reports to be received..."
    while True:
        # Loop forever
        time.sleep(60)
