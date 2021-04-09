---
title: "Command - MQTT Topics"
weight: 10
summary: "Command and control of a device using MQTT topics"
---

Command and control is the operation of sending a message to a device requesting it to perform some action. Optionally, the device can acknowledge that is has succeeded or failed to complete the action.

## Use Cases

- Interact with a peripheral, actuator, or operation of a device
  - _I want to turn the LED on or off on my device_
  - _I want to remotely restart the device_
- Request device data or state
  - _I want the device to publish the latest log file to a topic_
- Update device operating or saving configuration
  - _I want to increase the current frequency of telemetry emitted on my device_
  - _I want to change my devices saved configuration that will take effect on next restart_

## Reference Architecture

![Command and control via MQTT topics](architecture.svg)

- _AWS IoT Core_ is the MQTT message broker processing messages on behalf of the clients
- _Device_ is the IoT thing to be controlled
- _Application_ is the remote logic that issues commands

1. The _Device_ establishes an MQTT connection to the _AWS IoT Core_ endpoint, and the subscribes to the `device1/req` (request) topic. This is the topic where incoming messages will be received and processed.
1. The _Application_ established an MQTT connection to the _AWS IoT Core_ endpoint, and subscribes to the `device1/resp` (response) topic. This is the topic where the acknowledgement messages from the device will be received.
1. To send a command, the _Application_ publishes a message on the `device1/req` topic, and the device receives the message on its subscription to that topic and take some action.
1. (Optional) Once the command has been processed, the device then publishes the result of the action onto the `device1/resp` topic. The _Application_ receives the response message and reconciles the outstanding action.

{{% center %}}

```plantuml
@startuml
!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/InternetOfThings/all.puml
!includeurl AWSPuml/General/Client.puml

'Comment out to use default PlantUML sequence formatting
skinparam participant {
    BackgroundColor AWS_BG_COLOR
    BorderColor AWS_BORDER_COLOR
}
'Hide the bottom boxes
hide footbox

participant "<$IoTGeneric>\nDevice" as device
participant "<$IoTCore>\nMQTT Broker" as broker
participant "<$Client>\nApplication" as app

== Connect and subscribe ==
device -> broker : connect(iot_endpoint)
device -> broker : subscribe("device1/req")
app -> broker : connect(iot_endpoint)
app -> broker : subscribe("device1/resp")

== Command operation and (optional) response ==
app -> broker : publish("device1/req", "light: on", "id: 1111")
broker -> device : publish("device1/req", "light: on", "id: 1111")
device -> device : Turn on light
device -> broker : publish("device1/resp", "success", id: "1111")
broker -> app : publish("device1/resp", "success", id: "1111")
app -> app : reconcile("id: 1111")
@enduml
```

{{% /center %}}

### Assumptions

This implementation approach assumes the _Device_ is connected at all times, subscribed to a topic for incoming commands, and can receive and process the command. It also assumes that the _Device_ can notify the sending _Application_ that the command was received and processed if needed. Finally, it assumed that all three participants successfully receive, forward, and act up the message flows in either direction.

## Implementation

Both the _Application_ and the _Device_ use similar approaches to connecting, sending, and receiving messages. The code samples below are complete for each participant.

{{% notice note %}}
The code samples focus the _command_ design in general. Please refer to the [Getting started with AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html) for details on creating things, certificates, and obtaining your endpoint.

Also, only the code snippets needed to demonstrate the implementation are provided for clarity.
{{% /notice %}}

### Device

The _Device_ code focuses on connecting to _Broker_, subscribing to a topic to receive commands, and then publishing the outcome of each command back to the _Application_.

{{< tabs groupId="device-code">}}
{{% tab name="python" %}}
Please refer to this [pubsub sample](https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/pubsub.py) for more details.

Install SDK from PyPI: `python3 -m pip install awsiotsdk`

```python
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import sys
import time


# This sample uses the Message Broker for AWS IoT to send and receive messages
# through an MQTT connection. On startup, the device connects to the server,
# subscribes to a request topic, invokes a callback upon receipt of a message, and
# then responds on the response topic back to the calling application.

io.init_logging(getattr(io.LogLevel, "Info"), "stderr")

# Using globals to simplify sample code
# client_id = "device1"
# endpoint = "REPLACE_WITH_YOUR_ENDPOINT_FQDN"
# client_certificate = "PATH_TO_CLIENT_CERTIFICATE_FILE"
# client_private_key = "PATH_TO_CLIENT_PRIVATE_KEY_FILE"
# root_ca = "PATH_TO_ROOT_CA_CERTIFICATE_FILE"

client_id = "device1"
endpoint = "a2l4icd3ffczky-ats.iot.us-west-2.amazonaws.com"
client_certificate = "f11bb3f17c-certificate.pem.crt"
client_private_key = "f11bb3f17c-private.pem.key"
root_ca = "AmazonRootCA1.pem"

# Topic to subscribe for incoming commands
request_topic = "device1/req"
# Topic to send result of command
response_topic = "device1/resp"


# Callback's are the main method to asynchronously process MQTT connections
# and messages.

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(
        "Connection resumed. return_code: {} session_present: {}".format(
            return_code, session_present
        )
    )

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results["topics"]:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a command message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    global response_topic
    print("Received command from topic '{}': {}".format(topic, payload))

    # Call code to perform action on command, assert True for this example
    #################################################
    ############### COMMAND CODE HERE ###############
    #################################################
    # result = do_something(payload)
    result = True

    if result:
        message = "SUCCESS: command ran successfully from payload: {}".format(payload)
    else:
        message = "FAILURE: command did not run successfully from payload: {}".format(
            payload
        )
    print("Publishing message to topic '{}': {}".format(response_topic, message))
    mqtt_connection.publish(
        topic=response_topic, payload=message, qos=mqtt.QoS.AT_LEAST_ONCE
    )


if __name__ == "__main__":
    # Create SDK-based resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    # Create native MQTT connection from credentials on path (filesystem)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=client_certificate,
        pri_key_filepath=client_private_key,
        client_bootstrap=client_bootstrap,
        ca_filepath=root_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        clean_session=False,
        keep_alive_secs=6,
    )

    print("Connecting to {} with client ID '{}'...".format(endpoint, client_id))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(request_topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=request_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result["qos"])))

    # All logic happens in the on_message_received() callback, loop until
    # program stopped (e.g., CTRL+C)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Disconnect
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")
```

{{% /tab %}}
{{< /tabs >}}

## Considerations

### Lost, Duplicate, or Out-of-Order Messages

### Device Disconnected During Message Delivery
