"""
EventHub Producer (To Be Implemented by Eshi)
---------------------------------------------

This module sends batches of telemetry data to Azure Event Hub.
The Streamer calls producer.send(records, partition_key).

IMPORTANT:
- Do NOT ACK Redis unless EventHubProducer.send() succeeds.
- Use exponential backoff on retries.
- Handle max batch sizes — Event Hub has strict limits.
- Records passed in will be Python dicts.
"""

# TODO: Import necessary Azure Event Hub client classes
# from azure.eventhub import EventHubProducerClient, EventData

# TODO: Import retry logic (recommended: tenacity)
# from tenacity import retry, wait_exponential, stop_after_attempt

# TODO: Import typing modules (List, Dict, Any)
# from typing import List, Dict, Any

import os


class EventHubProducer:
    """
    Implement the logic to send telemetry to Azure Event Hubs.

    Expected behavior:
    - Initialize a connection to Event Hub via connection string + hub name.
    - Convert dict records to EventData objects.
    - Create batches and send them.
    - Retry sending with exponential backoff on transient failure.
    - Raise an exception on permanent failure.
    """

    def __init__(self, connection_string: str | None = None, eventhub_name: str | None = None):
        # TODO: Read connection string + hub name from env vars if not passed in
        # Example:
        #   connection_string = connection_string or os.getenv("EVENTHUB_CONNECTION_STRING")
        #   eventhub_name = eventhub_name or os.getenv("EVENTHUB_NAME")

        # TODO: Create EventHubProducerClient using the Azure SDK

        # TODO: Store client in `self._client`
        pass


    def send(self, records, partition_key):
        """
        Send a list of telemetry records to Azure Event Hub.

        Parameters:
        - records: List[dict]  → telemetry tuple objects
        - partition_key: str   → used to keep session data grouped

        Behavior:
        - Ignore calls with empty list.
        - Create a batch with partition_key.
        - Add EventData items to batch; flush and start a new batch if full.
        - Retry on failure (tenacity recommended).
        - Raise an exception if final attempt fails.
        """

        # TODO: If records is empty: return immediately

        # TODO: Create a batch
        # batch = self._client.create_batch(partition_key=partition_key)

        # TODO: For each record:
        #   convert dict to EventData
        #   try to add to batch
        #   if batch full → send & create new batch

        # TODO: After loop: send final batch

        pass
