# jitp_device.py - Demonstrates JITP (Just-In-Time Provisioning) device connection with automatic retry logic.
#
# On first connection, AWS IoT Core will reject the TLS handshake while it provisions the device.
# The device must retry after a short delay. On the second attempt, the device connects successfully.
#
# Prerequisites:
#   pip install awsiotsdk
#
# Usage:
#   python3 jitp_device.py \
#     --endpoint YOUR_IOT_ENDPOINT.iot.REGION.amazonaws.com \
#     --cert deviceCertAndCACert.crt \
#     --key deviceCert.key \
#     --root-ca AmazonRootCA1.pem \
#     --thing-name MyJITPDevice001 \
#     --topic test/jitp

import argparse
import time
import json
import sys
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

# Maximum number of connection attempts before giving up
MAX_RETRIES = 5
# Initial delay between retries in seconds (increases with backoff)
INITIAL_RETRY_DELAY = 3


def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. Error: {error}")


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"Connection resumed. Return code: {return_code}, Session present: {session_present}")


def connect_with_jitp_retry(endpoint, cert_filepath, pri_key_filepath, ca_filepath, client_id):
    """
    Attempt to connect to AWS IoT Core with JITP retry logic.

    On the first connection attempt with a new certificate signed by a registered CA,
    AWS IoT Core will:
    1. Verify the certificate against the registered CA
    2. Trigger the provisioning template to create Thing, activate cert, attach policy
    3. Reject the current TLS connection (provisioning happens asynchronously)

    The device must retry after a short delay. Subsequent attempts will succeed
    once provisioning is complete (typically 1-3 seconds).
    """

    # Create SDK resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    retry_delay = INITIAL_RETRY_DELAY

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- Connection attempt {attempt}/{MAX_RETRIES} ---")

        try:
            # Build MQTT connection using mutual TLS (X.509 certificate)
            mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=endpoint,
                cert_filepath=cert_filepath,
                pri_key_filepath=pri_key_filepath,
                client_bootstrap=client_bootstrap,
                ca_filepath=ca_filepath,
                on_connection_interrupted=on_connection_interrupted,
                on_connection_resumed=on_connection_resumed,
                client_id=client_id,
                clean_session=False,
                keep_alive_secs=30,
            )

            print(f"Connecting to {endpoint} with client ID '{client_id}'...")
            connect_future = mqtt_connection.connect()

            # Wait for connection to complete
            connect_future.result()
            print("Connected successfully!")
            return mqtt_connection

        except Exception as e:
            print(f"Connection attempt {attempt} failed: {e}")

            if attempt < MAX_RETRIES:
                print(f"JITP provisioning may be in progress. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # Exponential backoff with cap
                retry_delay = min(retry_delay * 2, 30)
            else:
                print("Max retries exceeded. JITP provisioning may have failed.")
                print("Verify that:")
                print("  - The CA certificate is registered and ACTIVE in AWS IoT Core")
                print("  - The provisioning template is attached to the CA")
                print("  - The device certificate's Common Name is unique")
                print("  - The Country field matches between device cert and CA cert")
                raise RuntimeError(f"Failed to connect after {MAX_RETRIES} attempts") from e


def publish_telemetry(mqtt_connection, topic, thing_name, message_count=5):
    """Publish sample telemetry messages after successful JITP connection."""

    print(f"\nPublishing {message_count} messages to topic '{topic}'...")

    for i in range(1, message_count + 1):
        payload = json.dumps({
            "deviceId": thing_name,
            "message": f"Hello from JITP device - message {i}",
            "timestamp": int(time.time()),
            "sequence": i
        })

        print(f"  Publishing message {i}/{message_count}: {payload}")
        mqtt_connection.publish(
            topic=topic,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
        time.sleep(1)

    print("All messages published.")


def main():
    parser = argparse.ArgumentParser(description="JITP Device - Connect and publish with automatic retry")
    parser.add_argument("--endpoint", required=True, help="AWS IoT Core endpoint")
    parser.add_argument("--cert", required=True, help="Path to device certificate (combined with CA cert)")
    parser.add_argument("--key", required=True, help="Path to device private key")
    parser.add_argument("--root-ca", required=True, help="Path to Amazon Root CA certificate")
    parser.add_argument("--thing-name", required=True, help="Thing name (must match certificate Common Name)")
    parser.add_argument("--topic", default="test/jitp", help="MQTT topic to publish to")
    parser.add_argument("--count", type=int, default=5, help="Number of messages to publish")

    args = parser.parse_args()

    # Initialize logging
    io.init_logging(getattr(io.LogLevel, "Info"), "stderr")

    try:
        # Connect with JITP retry logic
        mqtt_connection = connect_with_jitp_retry(
            endpoint=args.endpoint,
            cert_filepath=args.cert,
            pri_key_filepath=args.key,
            ca_filepath=args.root_ca,
            client_id=args.thing_name,
        )

        # Publish telemetry after successful connection
        publish_telemetry(mqtt_connection, args.topic, args.thing_name, args.count)

        # Disconnect
        print("\nDisconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected.")

    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
