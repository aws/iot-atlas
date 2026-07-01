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
