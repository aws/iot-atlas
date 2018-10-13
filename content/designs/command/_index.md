---
title: "Command"
weight: 11
draft: true
---
{{< synopsis-command >}}
<!--more-->

## Challenge
IoT solutions are expected to interact with devices in such a way that the solution, or people using the solution, may reliably ask devices to perform an action. Furthermore, this interaction must occur across intermittent networks, often using devices with limited resources. 

## Solution
IoT Solutions use the Command design to ask devices to perform an action and ensure reliable interactions by leveraging a simple concept: no requested action is deemed successful unless it is acknowledged as successful. 

The Command design shown in the following diagram can deliver this functionality.

![Command Design](command.png) 
([PPTx](atlas-command.pptx))
### Diagram Steps

1. A [device]({{< ref "/glossary#device" >}}) configures itself to communicate with a protocol endpoint so that Command messages can be sent and received.
2. A component of the solution publishes a [command message]({{< ref "/glossary#command-message" >}}) targeted at one or more devices. 
3. The server uses the protocol endpoint to send the Command message to each previously configured device.
4. Upon completion of the Command's requested action, the device publishes a command completion message to the server via the protocol endpoint. 

## Considerations
It is important to note that the Command design is not "telemetry in reverse". Instead the Command design addresses the challenge inherent for a solution that needs to reliably trigger actions on a device operating in a remote location.

When implementing this design, consider the following questions:

#### How can the solution track the progress of commands per device?
Each command should have a solution unique type and each command message should contain a globally unique message ID. The command message's ID allows the solution to track the status of distinct commands and the command type enables the diagnoses any potential issues across categories of commands over time.   

#### Do some commands in the solution run significantly longer than the norm?
When some commands run longer than the norm, a simple `SUCCESS`  or `FAIL` command completion message will not suffice. Instead the solution should leverage at least three command states: `SUCCESS`, `FAIL`, and `RUNNING`. `RUNNING` should be returned by the device on an expected interval until the command's completion. By using a `RUNNING` state reported on an expected interval a solution can determine when a long-running command actually fails quietly.  


#### Does a specific type of command require human-authorization?
When a command in a solution requires human approval before a device should take action, a human-workflow component should be added to the solution. This component would intercept commands of particular types and queue them up for human approval before actually sending them onward to a device.     

#### Does a type of command ever need to be rolled back to a previous state?
If a solution has some commands which may need to be rolled back, it is almost always easier to manage that rollback from the solution itself instead of expecting each device to understand and remember the rollback considerations. For example, a device is sent a command to move an actuator from a current, reported position of `0`&#176; to a position of `45`&#176;. The Device performs this command successfully. At a later moment in time the solution requires that the device go back to the previous state, the previous state is often easier to track in the solution itself versus expecting every device to track its former state(s). The rollback of this situation would be performed by the solution sending a command for the device to change position to `0`&#176;.  
In the case where rollbacks are necessary even when there is no connectivity to the server, the solution can leverage a [gateway]({{< ref "/designs/gateway" >}}) to record the former states of devices and to perform rollbacks based upon those values.  

## Example

Example showing receipt of a message, execution of an action, and acknowledgement of the action
`..mention something about use of QoS 1 or higher for MQTT for Command..`

    <Written scenarios>