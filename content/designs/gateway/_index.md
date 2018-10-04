---
title: "Gateway"
weight: 50
draft: true
---

{{< synopsis-gateway >}}
<!--more-->

## Challenge
[Endpoint]({{< ref "/glossary#endpoint" >}})s in an IoT solution are often not capable enough to connect directly to the internet nor are they operating on networks with direct access to the internet. Even with these constraints, obtaining data from and interacting with endpoints requires a mechanism of connectivity. 

## Solution
IoT solutions use the Gateway design to overcome the common constraints experienced by endpoints. In doing so a gateway enables reliable and secure communication with otherwise inaccessible endpoints. 

    <architecture diagram and step-wise description>

## Considerations

#### How should data be processed when the internet is unavailable?

A key thing to determine is the right action to take with the ongoing sensing data when the network is absent. In general, local processing of sensed data not yet delivered into the broader solution will follow a First-In-First-Out (aka. `FIFO`) algorithm. That being said, the answer *might* be different depending upon the data actually being sensed. In this case determining how the gateway's logging approach influences the actual reported data can help avoid future solution issues.  

The general categories of algorithms to consider are: **FIFO**, **Culling**, and **Aggregate** as shown in the following diagram.
![Message Processing Algorithms](algorithms.png)

**FIFO** – Straightforward to implement. In the above diagram this algorithm’s data arrives from the left and exits to the right when the allocated local storage is full. Examples of sensed data include: operations measurements and general-purpose telemetry.

**Culling** – Good for retaining absolute point values at a loss of curve smoothness. In the above diagram this algorithm’s data arrives from the left, and once local storage has been filled beyond a *culling point*, some sweeper logic then removes every other (or every `N`<sup>th</sup>) sample. Examples of sensed data include: [kW](https://en.wikipedia.org/wiki/Watt#Kilowatt), [Amperage](https://en.wikipedia.org/wiki/Amperage), [Voltage](https://en.wikipedia.org/wiki/Voltage), etc.

**Aggregate** – Good where the detailed shape of the curve is not as important as the minimum, maximum and average values over a period of time. In the above diagram this algorithm’s data conceptually arrives from the left and performs aggregation on the stored values once records have filled the storage past an *aggregation point*. Examples of sensed data include: [kWh](https://en.wikipedia.org/wiki/Kilowatt_hour), [insolation](https://en.wikipedia.org/wiki/insolation), [flow](https://en.wikipedia.org/wiki/Flow_measurement), [CPU time](https://en.wikipedia.org/wiki/CPU_time), [temperature](https://en.wikipedia.org/wiki/Temperature), [wind speed](https://en.wikipedia.org/wiki/Wind_speed), etc.

## Example
    <tbd written scenario>