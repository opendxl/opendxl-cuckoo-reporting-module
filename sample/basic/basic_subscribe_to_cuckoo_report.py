# This sample demonstrates how to register a callback to receive Event messages
# from the DXL fabric for the default Cuckoo report analysis. Once the callback is registered, the sample
# waits to receive Cuckoo report analyses.
import json
import logging
import os
import sys
import time

from dxlclient.callbacks import EventCallback
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig

# Import common logging and configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# The default Cuckoo report Event topic
EVENT_TOPIC = "/cuckoo/event/report"

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

# Create the client
with DxlClient(config) as client:

    # Connect to the fabric
    client.connect()

    # Create and add event listener
    class CuckooReportEventCallback(EventCallback):
        def on_event(self, event):
            # Print the payload for the received event
            print("Cuckoo report received: ")

            event_dict = json.loads(event.payload.decode(encoding="UTF-8"))
            print json.dumps(event_dict, sort_keys=True, indent=4, separators=(',', ': ')) + "\n"

    # Register the callback with the client
    client.add_event_callback(EVENT_TOPIC, CuckooReportEventCallback())

    # Wait until all events have been received
    print "Waiting for Cuckoo reports to be received..."
    while True:
        # Loop forever
        time.sleep(60)
