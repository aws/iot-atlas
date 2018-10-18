---
title: "Device Bootstrap"
weight: 15
draft: true
---

{{% synopsis-bootstrap %}}
<!--more-->

## Challenge
IoT solutions need devices to perform some sort of privilege escalation to go from zero privilege to a fully registered and operational device in that solution. While going from *no* privilege to *full* privilege there **should** be discrete and planned steps. Each step used to gain privilege must itself follow the approach of least privilege. Additionally, there may be existing identity and privilege systems which must be incorporated into the IoT solution. 

## Solution
An IoT solution can manage the challenges of bootstrapping a device by deconstructing those challenges into a flow across two distinct concepts: a *registration authority* and a *privilege escalator*.  

A **registration authority** is the component that validates an expected attribute, certificate, or token received from the device and then returns solution credentials for use by the device. A registration authority will at least be a collection of policies dictating the ability of un-registered devices to subscribe or publish to defined topics on the server.

A **privilege escalator** enables a device with short-lived, lower-privilege credentials to share more attributes about itself or to exhibit proper behavior before obtaining higher-privileges in the solution. A distinct privilege escalation step also enables the injection of human approval into the privilege escalation process, if the solution requires. 

Although there are situations where an implementation might combine registration with the ability to obtain fully escalated privileges, by breaking down the challenges as this design does, each challenge can be addressed distinctly, using new or legacy systems. 

The Device Bootstrap design shown in the following diagram can deliver this functionality.

![Device Bootstrapping](bootstrap.png)

### Diagram Steps
1. A device registers with the registration authority using basic credentials or by sending some matching attribute or token.
2. The registration authority validates the authenticity of the credentials, attribute or token, registers the device, and returns short-lived credentials to the device.
3. A device uses the short-lived credentials to contact the privilege escalator and to share more information about itself
4. The privilege escalator determines the device's type and determines if the device should be authorized in the IoT solution. If the device is authorized, the privilege escalator returns long-lived credentials associated with privileges corresponding to the device's purpose within the IoT solution.
5. A device uses the long-lived privileges to subscribe and publish to the device's [messaging topic]({{< ref "/glossary#messaging-topic" >}})s via the server's protocol endpoint.

## Considerations
When implementing this design, consider the following questions:

#### Does the device's manufacturing process create and place the initial token on the device?
If **no**, then the device must have a mechanism to receive a secure token or certificate after the device is manufactured. In this case, it is important that the initial token is used to enable only the minimal privileges necessary to register with the solution. Once the registration authority validates the initial token, the rest of the steps of this design should be followed.

If **yes**, the device can be manufactured in a secure manner and the need for a Registration Authority can be reduced if not removed altogether. This is easy to say and difficult to achieve as many manufacturing processes are purposefully disconnected from the cloud. Regardless, since the solution may have an entire step removed when keys are introduced by the manufacturer, the customer experience and overall system simplicity will benefit.  

#### Does the registration authority need to support custom authorization integration with an existing customer solution?
If **yes**, the design's registration authority step can be implemented using an Application Programming Interface ([API](https://en.wikipedia.org/wiki/Application_programming_interface)) in front of an existing customer solution. This API can then perform the registration authority job while leveraging the customer's existing solution.

## Examples

    <tbd written scenario>