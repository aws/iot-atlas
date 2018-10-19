---
title: "Software Update"
weight: 70
draft: true

---

{{< synopsis-software-update >}}
<!--more-->

## Challenge
IoT solutions are required to provide a mechanism for devices to update their own software. Supporting software updates without human intervention is both critical for scaling solutions to millions of devices and for delivering a great customer experience. However, achieving a full update of large sets of devices in a secure, scalable, and reliable fashion requires a solution that can scale to meet device load, a resilient command mechanism, and a way of tracking the state of the the entire fleet of devices. 

## Solution
IoT solutions that leverage the [Command]({{< ref "/designs/command" >}}) and [Device State Replica]({{< ref "/designs/device_state_replica" >}}) designs alongside a globally available and scalable storage solution are able to meet all the challenges inherent in updating the software of devices in a large fleet. 

The Software Update pattern shown in the following diagram can deliver this functionality. 

![Software Update](software-update.png)

### Diagram Steps
1. A device subscribes to the delta [messaging topic]({{< ref "/glossary#message-topic" >}}) `state/deviceID/update/delta` upon which device-related state change messages will arrive.
2. An application obtains the new software distribution and places that into a storage solution accessible to production devices. 
3. An application identifies a device that should receive the new software and publishes a desired state message to the device's topic `state/deviceID/update`. The desired state message contains a software update URL different form the device's current software version URL.
4. The device state replica tracking this device records the desired device state in a persistent data store and publishes a delta message to the topic `state/deviceID/update/delta` that is sent to the device.
5. The device receives a delta message that acts as the 'software update' command. Specifically, this message conveys the change between the current software version URL and the new URL
6. The device obtains the new software update URL from the delta message.
7. The device downloads the new software and applies the software locally.
8. The device publishes an acknowledgement message reflecting the software version the device is now using to the update topic `state/deviceID/update` and a device state replica tracking this device records the new state in a persistent data store. 
9. The device state replica publishes a message to the `state/deviceID/update/accepted` topic. The software update is now considered complete.

## Considerations
When implementing this design, consider the following questions:

#### How does the targeted device and only that device obtain the software update from the given URL?  
The solution can ensure that only the device targeted for a software update can obtain the update by using a **pre-signed URL** or a **temporary credential**. Each approach has different considerations. 

**Pre-signed URL** - the benefit of a pre-signed URL is that it constrains the ability for a device to download a software update within a period of time and by devices with specific public IP addresses. The negative of this approach arises when the device downloading the the update does not have a publicly resolvable IP address. Without a publicly resolvable IP address the solution can only place a time boundary on the interaction with the software update. The practitioner of a solution may or may not find this acceptable.    

**Temporary Credential** - a device interacts with the solution to obtain a temporary credential associated with only the privilege of accessing the storage solution to download the update. The benefit of using a temporary credential is that only the device with that credential can access the update, even when the device does not have a publicly resolvable IP address. The slight negative of this approach is that it requires the device and solution to be more complex because the device must go through a separate process to obtain temporary credentials.

## Example
Example showing a targeted device receiving and executing an "upgrade thyself" Command. Specifically, the device will obtain new firmware, perform an upgrade on itself, and acknowledge success.

    <tbd written scenario>