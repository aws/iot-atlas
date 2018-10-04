---
title: "Device State Replica"
weight: 20
draft: true
---

{{< synopsis-state-replica >}}
<!--more-->

{{% notice note %}}
**TODO:** Revise Considerations to allow CoAP, MQTT, and AMQP transport protocols to fit conceptually.
{{% /notice %}}

## Challenge
IoT solutions are expected to interact with devices to perform and track device state changes. There are two ways this challenge manifests. First, even when experiencing intermittent network connectivity the solution needs the device to perform an action that changes the state of a device, and second the device needs the solution to reflect a state change which has occurred on the device.

## Solution
IoT solutions that leverage the Device State Replica design are able to manage device-related state changes in a reliable, scalable, and straightforward fashion. 

The Device State Replica design describes how to replicate a device's current state, desired future state, and the difference between current and desired states. The Device State Replica design is similar to [Command]({{< ref "/designs/command" >}}) in that both use [message]({{< ref "/glossary#message" >}})s as triggers for actions and acknowledgement messages when actions are complete. However, the Device State Replica design goes farther than simple acknowledgments, by taking a prescriptive approach to both the management of device-related state and how the state and changes are communicated. 

### Component-to-device State Replica

An IoT solution should leverage the following design when a *component* of the IoT solution is the source of the desired state change and that change should be replicated in a device.

{{% notice note %}}
**TODO:** Revise Diagram to allow CoAP, MQTT, and AMQP transport protocols to fit conceptually.  
{{% /notice %}}

![Component-to-device State Replica](c2d-state.png)

### Component-to-device Diagram Steps

1. A device reports initial device state by publishing that state as a [message]({{< ref "/glossary#message" >}}) to the update topic `deviceId/state/update`.
2. The Device State Replica tracking this device reads the message from the topic and records the device state in a persistent data store.
3. A device subscribes to the delta messaging topic `deviceId/state/update/delta` upon which device-related state change messages will arrive.
4. A component of the solution publishes a *desired state* message to the topic `deviceId/state/update`and the Device State Replica tracking this device records the desired device state in a persistent data store.
5. The Device State Replica publishes a delta message to the topic `deviceId/state/update/delta` and the Server the message to the device.
6. A device receives the delta message and performs the desired state changes.
7. A device **publishes** an acknowledgement message reflecting the new state to the update topic `deviceId/state/update` and the Device Shadow tracking this device records the new state in a persistent data store.
8. The Device State Replica publishes a message to the `deviceId/state/update/accepted` topic.
9. A component of the solution can now request the updated state

### Device-to-component State Replica

An IoT solution should leverage the following design when the *device* is the source of the state change that should be communicated to components of the IoT solution.

![Device-to-component State Replication](#)

### Device-to-component Diagram Steps
1. A device reports initial device state by publishing that state as a message to the update topic `deviceId/state/update`.
2. A device detects that its own state has changed and reports a new state value to the update topic `deviceId/state/update`.

## Considerations

#### `..need more considerations..`

## Example
    <tbd written scenario>