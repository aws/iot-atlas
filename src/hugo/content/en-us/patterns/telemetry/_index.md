---
title: "Telemetry"
weight: 80
---

{{< synopsis-telemetry >}}

<!--more-->

## Challenge

IoT solutions need to reliably and securely receive data measured in a remote environment by different devices, potentially using different protocols. Additionally, once the measured data is received, the solution needs to process and route the sensed data for use by components of the solution.

## Solution

IoT solutions use the Telemetry pattern to ensure the delivery of sensed data across intermittent networks by supporting adept communication protocols, to provide scalable reception of data at different reporting frequencies and volumes, and to route data for use by other components.

The Telemetry pattern shown in the following diagram can deliver this functionality.

![Telemetry pattern](telemetry.png)

### Diagram Steps

1. The device obtains a measurement from a sensor operating in an environment remote from the IoT solution.
2. The device publishes a message to the [message topic]({{< ref "/glossary/vocabulary#message-topic" >}}) `telemetry/deviceID` containing the measurement. This message is sent via a transport protocol to a protocol endpoint made available by the Server.
3. The Server may then apply one or more [rule]({{< ref "/glossary/vocabulary#rule" >}})s to messages in order to perform fine-grained routing upon some or all of the message's measurement data. The routing can send a message to another component of the solution.

## Considerations

The **Telemetry** pattern is commonly engaged when a project has the requirement to "stream data from a device". Furthermore, when implementing an IoT solution, the word _telemetry_ is often used both as a way of describing the above pattern diagram _and_ a shorthand description for the entire collection of challenges inherent in sensing and sending data from a remote location into a larger solution. These considerations focus on topics which usually relate to implementing the above diagram.

When implementing this pattern, consider the following questions:

#### What is the desired _sense-to-insight_ or _sense-to-action_ processing latency of telemetry messages in the IoT solution?

IoT solutions with processing latency requirements at the level of **&micro;-seconds or milliseconds** should perform that processing on the device itself or possibly on a device [gateway]({{< ref "/patterns/gateway" >}}) connected to the device.  
IoT solutions with processing latency requirements at the level of **Seconds**, **Minutes**, or even **Hours** should perform that processing on the cloud by default.  
In general processing of messages in "seconds" through "low minutes", should be performed by components connected directly to the protocol endpoint. Commonly a component's processing will be triggered by the arrival of messages that match certain criteria.  
Processing telemetry from "low minutes" through "hours" should be performed in an asynchronous fashion. When messages arrive that match desired criteria events will most often be placed in a processing queue and a component will perform the necessary work. Once complete, often the component will emit a message to a "work complete" [message topic]({{< ref "/glossary/vocabulary#message-topic" >}}).

#### Are there lessons learned that make telemetry data easier to process in the IoT solution?

**Solution Unique Device IDs** – Each device in a solution should have a _solution unique_ ID. Although this ID does not need to be truly globally unique each device should have an ID that is and will forever be unique within the IoT solution. By embracing solution unique device IDs, the IoT solution will be better able to process and route the sensed data for use by components within the solution.  
**Early Time-stamping** – The earlier sensed data obtains discrete timestamps in an IoT solution, the earlier more nuanced processing and analysis of that sensed data can occur.  
**Closed Window Calculations** - Tracking a device's `last_reported` timestamp could determine if/when an aggregation window is able to be considered _closed_. Any closed window calculations can then be easily and confidently cached throughout an IoT solution. These cached calculations often dramatically increase performance of the _sense-to-insight_ or _sense-to-action_ processing latency of the IoT solution.

#### How should large messages be handled?

Large messages are defined in this pattern as any message larger than the transport protocol natively supports. Large messages require an additional question to be answered, **"Can a secondary protocol be used?"**

If **yes**, HTTPS is recommended.  
If **no**, then the large message must be broken into parts, each part should have a unique part identifier and each part should be small enough to be sent using the transport protocol.

#### How should large messages be sent when using a secondary protocol?

If large messages must be **delivered as soon as possible**, the large message can be uploaded directly to a globally available, highly durable object storage service.

If large messages **can be sent in batches**, each message should be saved as a part of a batch until the batch can be sent. Since storage on a device is often a constrained resource, the batch processing of messages should consider the same [algorithmic trade-offs]({{< ref "/patterns/gateway#how-should-the-gateway-process-data-when-the-network-to-the-server-is-unavailable" >}}) as a device acting as a [gateway]({{< ref "/patterns/gateway" >}}).

#### What are the sample vs. reporting frequencies of a device?

**Sample frequency** is the frequency at which sensed data is retrieved, or _sampled_ from an attached [sensor]({{< ref "/glossary/vocabulary#sensor" >}}).

**Reporting frequency** is the frequency at which sample data stored on the device is sent into the broader IoT solution.

Device-based code will either obtain sensed data and queue it for delivery or deliver the sensed data immediately. These two different behaviors are often discussed as the _difference between the sample frequency and the reporting frequency_. When the sample and reporting frequencies are equal and aligned, all sensed data is expected to be delivered immediately. When the two frequencies are different, choosing the correct logging algorithm for the enqueued data must be considered.

The expected values for these two frequencies are important when determining the scale and cost of an IoT solution.

#### Does the order of inbound messages need to be maintained?

First, solutions should only depend on order when it is absolutely necessary.

If ordering is **not required**, then the solution can process messages from the topic immediately upon arrival.  
If ordering is **required**, this follow-on question needs an answer, "On how long of a time horizon does a component of the solution require ordered messages?"

If the follow-on answer is "less than a one second horizon on a single topic", the solution can gather messages from a topic `foo` into a buffer, then after each tick of the clock, the buffer is sorted and messages are emitted in order to another topic `foo/ordered`.
If the answer is "greater than a one second horizon", the IoT solution should write every record to an [ordered store]({{< ref "/glossary/vocabulary#ordered-store" >}}). Any component of the solution that **requires** messages to always be in-order, can now read and get updates from the ordered store.

#### What are some of the cost drivers of telemetry in an IoT solution?

Usually the most common drivers of cost in an IoT solution are the number of devices, the device sample and reporting frequencies, the necessary _sense-to-insight_ or _sense-to-action_ telemetry processing latency, the [device data density]({{< ref "/glossary/vocabulary#device-data-density" >}}) and finally the retention duration of [telemetry archiving]({{< ref "/patterns/telemetry_archiving" >}})

#### Does each device "actively un-align" its reporting interval with other devices?

A common mistake that has a large impact, occurs when all devices in an IoT solution or fleet are configured with the same reporting frequencies. To avoid the [constructive interference](http://en.wikipedia.org/w/index.php?title=Constructive_interference) hidden in this simple behavior, a device should start its reporting interval only after it wakes and a random duration has passed. This start-time randomness produces a smoother stream of sensed data flowing into the solution by avoiding the constructive interference that occurs when devices recover from inevitable regional network or other solution-impacting outages.

#### What should a device do when it cannot connect to its default IoT solution endpoint?

**Expected duration** – When a device cannot connect with the default IoT solution endpoint for an expected duration, the device should have a configured behavior for _device message queuing_. This queueing might be the same answer provided when determining the difference between the devices sensing and reporting frequencies. Furthermore, any device with the ability to perform device message queueing should consider the same algorithmic trade-offs as a device acting as a device [gateway]({{< ref "/patterns/gateway" >}}). These trade-offs arise when local storage is not enough to store all messages for the expected duration and will impact the sensed data. The common categories of algorithm to consider are: **[FIFO](<https://en.wikipedia.org/wiki/FIFO_(computing_and_electronics)>)**, **Culling**, and **Aggregate**.

**Disaster-level duration** – When a device cannot connect with the default IoT solution endpoint for a disaster-level duration, then a _regional fail-over_ is required. To achieve this, first a device must have a pre-configured fail-over endpoint. Then when a device reorients itself to the fail-over endpoint, the device is **already registered** with the new region, and it already has the proper credentials, the device simply starts sending messages as if the new endpoint is the default. Otherwise when the device is **not registered** with the new region, the device will need to complete a [device bootstrap]({{< ref "/patterns/device_bootstrap" >}}) with the new regional endpoint prior to sending messages.

#### How can messages be stored and available for future replay in the IoT solution?

This can be accomplished with the [telemetry archiving]({{< ref "/patterns/telemetry_archiving" >}}) pattern.

## Examples

### Telemetry message creation, delivery, and routing.

A detailed example of the logic involved to gather sensor data and send it through an IoT solution.

#### A device samples a sensor and creates a message

Either with code on the device or code operating in a device [gateway]({{< ref "/patterns/gateway" >}}), a device samples a sensor in a fashion similar to the following pseudocode:

```python3
device_id = get_device_id()
while should_poll():  # loop until we should no longer poll sensors
    for sensor in list_of_sensors:
        # get timestamp of this 'sensor' reading
        ts = get_timestamp()
        # read the current sensor's value
        value = sensor.read_value()
        # add sensed data to message
        msq = create_message(device_id, sensor.get_id(), ts, value)
        send_sensor_message(msg)  # send or enqueue message
    # sleep according to the sample frequency before next reading
    sleep(<duration>)
```

The `create_message` pseudocode function above creates a message based upon the `device_id`, the `sensor_id`, the timestamp `ts`, and the `value` read from the sensor.

#### Device formats a message

Many existing solutions will have a message format already implemented. However, if the message format is open for discussion, JSON is recommended. Here is an example JSON message format:

```json
{
  "version": "2016-04-01",
  "deviceId": "<solution_unique_device_id>",
  "data": [
    {
      "sensorId": "<device_sensor_id>",
      "ts": "<utc_timestamp>",
      "value": "<actual_value>"
    }
  ]
}
```

#### Device delivers a message

Once the sensed data is placed in a message, the device publishes the message to the remote protocol endpoint on a reporting frequency.

When reporting messages using the MQTT protocol, messages are sent with topics. Messages sent by a device with the topic `telemetry/deviceID/example` would be similar to the following pseudocode.

```python
# get device ID of the device sending message
device_id = get_device_id()
# get the collection of unsent sensor messages
sensor_data = get_sensor_messages()
# the device's specific topic
topic = 'telemetry/' + device_id + '/example'
# loop through and publish all sensed data
while record in sensor_data:
    mqtt_client.publish(topic, record, quality_of_service)
```

#### Messages sent to subscribers

Each published messages traverses the network to the protocol endpoint. Once received, the server software makes each message available to interested parties. Parties will often register their interest by subscribing to specific message topics.

In addition to having components in the IoT solution subscribe directly to a messaging topic, some IoT solutions have a rule engine that allows a rule engine to subscribe to inbound messages. Then, on a message-by-message basis, rules in a rule engine can process messages or direct messages to other components in the IoT solution.
