# This sample demonstrates how to register a callback to receive Event messages
# from the DXL fabric for the compressed Cuckoo report analysis. Once the callback is registered, the sample
# waits to receive compressed Cuckoo report analyses.

import logging
import os
import sys
import time
import zlib

from dxlbootstrap.util import MessageUtils
from dxlclient.callbacks import EventCallback
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig

# Import common logging and configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# The topic to publish to
EVENT_TOPIC = "/cuckoo/event/report/zip"

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

# Create the client
with DxlClient(config) as client:

    # Connect to the fabric
    client.connect()

    #
    # Register callback and subscribe
    #

    # Create and add event listener
    class CuckooReportEventCallback(EventCallback):
        def on_event(self, event):
            # decompress zipped Cuckoo report
            event_decompressed_payload = zlib.decompress(event.payload, 31)

            # Print the payload for the received event
            print("Cuckoo compressed report received: " + MessageUtils.dict_to_json(
                MessageUtils.json_to_dict(event_decompressed_payload), pretty_print=True))

    # Register the callback with the client
    client.add_event_callback(EVENT_TOPIC, CuckooReportEventCallback())

    # Wait until all events have been received
    print "Waiting for Cuckoo compressed reports to be received..."
    while True:
        # Loop forever
        time.sleep(60)
