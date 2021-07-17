---
title: "Fleet Provisioning - Bootstrap Certificate"
weight: 10
summary: "Command and control of a device using MQTT topics"
---

Command and control is the operation of sending a message to a device requesting it to perform some action. Optionally, the device can acknowledge that is has succeeded or failed to complete the action.

{{% notice note %}}
This implementation focuses on the use of MQTT topics for performing request and response patterns (e.g. command and control). Please refer to the [Designing MQTT Topic for AWS IoT Core](https://docs.aws.amazon.com/whitepapers/latest/designing-mqtt-topics-aws-iot-core/designing-mqtt-topics-aws-iot-core.html), specifically the _Using the MQTT Topics for Commands_ section. This white paper provides alternative topic patterns that go beyond the scope of this implementation.
{{% /notice %}}

## Use Cases

- Near real-time action taken when command issued to a device
  - _I want the light to turn on when I press a button from my mobile app_
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

1. The _Device_ establishes an MQTT connection to the _AWS IoT Core_ endpoint, and then subscribes to the `cmd/device1/req` (request) topic. This is the topic where incoming messages will be received and processed.
1. The _Application_ establishes an MQTT connection to the _AWS IoT Core_ endpoint, and then subscribes to the `cmd/device1/resp` (response) topic. This is the topic where the acknowledgement messages from the device will be received.
1. To send a command, the _Application_ publishes a message on the `cmd/device1/req` topic, and the device receives the message on its subscription to that topic and take some action.
1. (Optional) Once the command has been processed, the device then publishes the result of the action onto the `cmd/device1/resp` topic. The _Application_ receives the response message and reconciles the outstanding action.

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
device -> broker : subscribe("cmd/device1/req")
app -> broker : connect(iot_endpoint)
app -> broker : subscribe("cmd/device1/resp")

== Command operation and (optional) response ==
app -> broker : publish("cmd/device1/req", "light: on", "id: 1111")
broker -> device : publish("cmd/device1/req", "light: on", "id: 1111")
device -> device : Turn on light
device -> broker : publish("cmd/device1/resp", "success", id: "1111")
broker -> app : publish("cmd/device1/resp", "success", id: "1111")
app -> app : reconcile("id: 1111")
@enduml
```

{{% /center %}}

### Assumptions

This implementation approach assumes the _Device_ is connected at all times, subscribed to a topic for incoming commands, and can receive and process the command. It also assumes that the _Device_ can notify the sending _Application_ that the command was received and processed if needed. Finally, it assumed that all three participants successfully receive, forward, and act up the message flows in either direction.

## Implementation

Both the _Application_ and the _Device_ use similar approaches to connecting, sending, and receiving messages. The code samples below are complete for each participant.

{{% notice note %}}
The code samples focus on the _command_ design in general. Please refer to the [Getting started with AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html) for details on creating things, certificates, and obtaining your endpoint. The code samples below are used to demonstrate the basic capability of the _Command_ pattern.
{{% /notice %}}

### Device

The _Device_ code focuses on connecting to _Broker_ and then subscribing to a topic to receive commands. Upon receipt of a command, the _Device_ performs some local action and then publishes the outcome (success, failure) of the command back to the _Application_, which then can reconcile the command.

The _Device_ will continue to receive and respond to commands until stopped.

{{< tabs groupId="device-code">}}
{{% tab name="python" %}}
Please refer to this [pubsub sample](https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/pubsub.py) for more details.

- Install SDK from PyPI: `python3 -m pip install awsiotsdk`
- Replace the global variables with valid endpoint, clientId, and credentials
- Start in a separate terminal session before running the _Application_: `python3 client.py`

```python
# client.py - Demonstrates waiting for a command to be evaluated and processed
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
client_id = "device1"
endpoint = "REPLACE_WITH_YOUR_ENDPOINT_FQDN"
client_certificate = "PATH_TO_CLIENT_CERTIFICATE_FILE"
client_private_key = "PATH_TO_CLIENT_PRIVATE_KEY_FILE"
root_ca = "PATH_TO_ROOT_CA_CERTIFICATE_FILE"


# Topic to subscribe for incoming commands
request_topic = "cmd/device1/req"
# Topic to send result of command
response_topic = "cmd/device1/resp"


# Callback's are the main method to asynchronously process MQTT events
# using the device SDKs.

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(
        f"Connection resumed. return_code: {return_code} session_present: {session_present}"
    )

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe results: {resubscribe_results}")

    for topic, qos in resubscribe_results["topics"]:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")


# Callback when the subscribed topic receives a command message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    global response_topic
    print(f"Received command from topic '{topic}': {payload}")

    # Action to perform on receiving a command, assert True for this example
    #################################################
    ############### COMMAND CODE HERE ###############
    #################################################
    # result = do_something(payload)
    result = True

    if result:
        message = f"SUCCESS: command ran successfully from payload: {payload}"
    else:
        message = f"FAILURE: command did not run successfully from payload: {payload}"
    print(f"Publishing message to topic '{response_topic}': {message}")
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

    print(f"Connecting to {endpoint} with client ID '{client_id}'...")

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print(f"Subscribing to topic '{request_topic}'...")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=request_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print(f"Subscribed with {str(subscribe_result['qos'])}")

    # All logic happens in the on_message_received() callback, loop until
    # program stopped (e.g., CTRL+C)
    print(f"Listening for commands on topic: {request_topic}")
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

### Application

The _Application_ code connects to the Broker and subscribes to the _Device_'s response topic. It then waits for a command to be entered and sends that to the _Device_'s request topic.

{{< tabs groupId="device-code">}}
{{% tab name="python" %}}

Please refer to this [pubsub sample](https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/pubsub.py) for more details.

- Install SDK from PyPI: `python3 -m pip install awsiotsdk`
- Replace the global variables with valid endpoint, clientId, and credentials
- Start in a separate terminal session after the _Device_ code is running: `python3 application.py`

```python
# application.py - Demonstrates sending commands to a device
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import sys
import time


# This sample uses the Message Broker for AWS IoT to send and receive messages
# through an MQTT connection. On startup, the app connects to the server,
# subscribes to a response topic which is invoked via a callback upon receipt of a message.
# Commands are sent

io.init_logging(getattr(io.LogLevel, "Info"), "stderr")

# Using globals to simplify sample code
client_id = "app1"
endpoint = "REPLACE_WITH_YOUR_ENDPOINT_FQDN"
client_certificate = "PATH_TO_CLIENT_CERTIFICATE_FILE"
client_private_key = "PATH_TO_CLIENT_PRIVATE_KEY_FILE"
root_ca = "PATH_TO_ROOT_CA_CERTIFICATE_FILE"

# Topics for the test target device
target_device = "device1"
# Topic to send a command to the device
request_topic = f"cmd/{target_device}/req"
# Topic to subscribe for command responses
response_topic = f"cmd/{target_device}/resp"


# Callback's are the main method to asynchronously process MQTT events
# using the device SDKs.

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(
        f"Connection resumed. return_code: {return_code} session_present: {session_present}"
    )

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe results: {resubscribe_results}")

    for topic, qos in resubscribe_results["topics"]:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")


# Callback when the subscribed topic receives a command message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    global response_topic, target_device

    print(f"Received command response on topic '{topic}' with payload: {payload}")

    # Action to perform on device completing the command
    #################################################
    ############### COMMAND CODE HERE ###############
    #################################################
    # result = reconcile_command(payload)


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

    print(f"Connecting to {endpoint} with client ID '{client_id}'...")

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe to the device response topic
    print(f"Subscribing to topic '{response_topic}'...")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=response_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print(f"Subscribed with {str(subscribe_result['qos'])}")

    # All logic happens in the on_message_received() callback, loop until
    # program stopped (e.g., CTRL+C)
    try:
        while True:
            command = input(f"Enter command to send to {target_device}: ")
            print(f"Publishing command to topic '{request_topic}': {command}")
            mqtt_connection.publish(
                topic=request_topic, payload=command, qos=mqtt.QoS.AT_LEAST_ONCE
            )
            # Wait for response text before requesting next input
            time.sleep(2)

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

This implementation covers the basics of a command and control pattern. It does not cover certain aspects that may arise in production use.

### Duplicate, or Out-of-Order Messages

In normal operation, MQTT command messages may be lost between the _application_ and the _broker_, or between the _broker_ and the _device_. This can be caused by QoS settings, retransmissions or retries from the publishers or _broker_, or other internal application errors such as a blocked thread.

For duplicate or out-of-order message, a command should nominally only be processed once, the inclusion of a unique transaction id (TID) [(see _Command_ pattern examples)]({{< ref "/patterns/command/#examples" >}}) in both the request and response provides the _application_ to resolve the message. For duplicate messages, the _device_ can keep a list of recently processed messages and only act on new TIDs.

For out-of-order messages, the TID can encompass either an incrementing number or sequence, and the _device_ can track the order of messages received. Another approach could be to use a [timestamp](https://en.wikipedia.org/wiki/Timestamp) for a TID where the _device_ tracks the last processed message and if it receives one with a timestamp earlier, can discard or otherwise act on the message out of order.

When dealing with _command_ messages that need to be processed in a certain order (e.g., **A**, then **B**, then **C**), both the _device_ and _application_ should agree on a state of commands and respond accordingly if they come out of order. For instance, if a _device_ receives command **A** (valid) and then command **C** (invalid as the next command should have been **B**), it should report back a failure and notify the calling _application_ of it's current state.

### Lost Messages or Device Disconnected During Delivery

Another consideration is how a command message should be tracked and processed if it is never delivered. It is common for IoT devices to be offline to the _broker_ for periods of time. This could be due to the device being turned off, local or widespread ISP outages, or due to intermittent network issues. Also, even with the use of a [QoS of 1](https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html#mqtt-qos), there is still the potential for message loss.

The _application_ should have logic to track outstanding commands, such as a timer to retransmit the command if it does not receive a response in a certain period of time with [retry logic](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/). In the event the device does not respond within a set period of time, the _application_ can raise an error for device connectivity.

From a _device_ perspective, if it is disconnected during the processing of command or series of commands, the _device_ should publish an error once it reconnects. This can give the _application_ making the request context for how to proceed.

### Fan-out to a Group of Related Devices

This implementation is focused on a single _application_ and _device_ interaction. Some use cases may have a single command affecting multiple devices. For instance, an _application_ may request all warning lights to turn on a factory floor in the event of an emergency. Or, it could be requesting a fleet of devices to report back their current configuration and status.

For a small group of _devices_, an approach could be for the _application_ to send an individual command to each device and reconcile the response.

However, when the target _device_ group is large, this would require the _application_ to send 1 per-_device_. In this case, _devices_ could subscribe to a common topic for fan-out types of messages, and the application only needs to send out a single message and reconcile the individual _device_ responses.

For instance, `device1`, `device2`, and `device3`, can all subscribe to the topic `device_status/request`. When the _application_ publishes a message on that topic, each device will receive a copy of the message, can act upon it, and each can the publish their response to a common `device_status/response` topic. The _application_ or [AWS IoT Rules Engine](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rules.html) can then reconcile the responses. This pattern is covered in the [Designing MQTT Topics for AWS IoT Core whitepaper](https://docs.aws.amazon.com/whitepapers/latest/designing-mqtt-topics-aws-iot-core/mqtt-design-best-practices.html).
