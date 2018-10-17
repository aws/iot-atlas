---
title: "Home"
---
# Welcome

Welcome to the IoT Atlas, where successful journeys using the internet of things rely on a few maps.

The most successful Internet of Things (aka IoT) projects progress from prototype, through pilot and limited production toward an identified business outcome delivered in production. The IoT Atlas attempts to support your project by explaining the why, what, and who of commonly used, modern IoT designs.

# Overview
Many IoT designs now being used globally are well-worn and time-tested but not widely known. The designs often come from mature domains such as *sensor networks*, *control system architectures*, *machine-to-machine networks*, and *device development*. But the lack of visibility of those mature designs is causing many people to [reinvent the wheel](https://en.wikipedia.org/wiki/Reinventing_the_wheel) for their solution, when they'd prefer not. Further complicating the matter for experienced practitioners, even when a long-standing design is known, the design often needs to be revised to take into account cloud development concepts. 

The IoT Atlas is an attempt to create an educational resource for both new and long-time practitioners of internet of things solutions. It is an attempt to update and expand upon well-worn designs with the presumption that today building "Internet of Things" solutions almost always means that "a hyper-scale cloud is available" to practitioners building that solution. Taking the stance that solutions development can rely upon the existence of a hyper-scale cloud does not imply the IoT Atlas' designs must be connected in order to operate. Instead the designs attempt to leverage the strength of a fleet of devices operating locally in remote environments for long periods of time **and** the cloud's strengths of massive scale, global ubiquity, and solution agility. The designs can then be used to build bar-raising solutions that expect intermittent, long-duration, or primarily-disconnected network outages as a fundamental influence of their designed components. Essentially the designs herein follow the IoT philosophy that *the edge completes the cloud*. 
 
By starting from this perspective, we are attempting to create an atlas that supports an understanding of even the most complex IoT considerations. It would be great to have you join us and [contribute](https://github.com/aws/iot-atlas/blob/master/CONTRIBUTING.md) your ideas for designs, considerations, and examples to this journey. 

# Organization

Each design attempts to cover one concept, cover it well, and, when it makes sense, describe how the current design will interoperate with other designs. When a new concept is necessary to better understand a design, the concept will be introduced just in time in the design and also referenced in the [glossary]({{< ref "/glossary" >}}). 
 
To meet the bar for publication, a fully-formed IoT Atlas design will provide a simple one or two sentence description, a concise description of the IoT challenge the design addresses, a simple non-vendor-specific architectural diagram and process flow, the personae commonly interested in and impacted by the capabilities delivered by the design, and key implementation considerations. The key considerations of a design are to be documented in the IoT Atlas itself and also through links to papers that provide additional context; such as, white-papers, blog posts, and generally any vetted content on the internet which best conveys what should be considered.  

# Design Considerations

Each design attempts to describe the pattern at a level of abstraction that incorporates as many details as possible, but no more than necessary. Of course this is a hard balance to achieve and will surely adjust over the lifetime of this effort. Initially the IoT Atlas will describe designs just **above** the details of which communication protocol or which programming language might be used in an implementation. For example, the [Telemetry](/designs/telemetry) design is purposefully described just above the details of [CoAP](http://coap.technology/), [MQTT](http://mqtt.org/), or [AMQP](https://www.amqp.org/product/architecture) and yet someone familiar with these protocols would still understand the design's concept without any or only a slight amount of transformation. It is unlikely that all possible perspectives can be incorporated, but the goal of describing designs at this level of abstraction is in line with the primary intent to help practitioners understand the design across the widest possible set of IoT solutions.

Designs in the IoT Atlas will use the concept of [message topics]({{< ref "/glossary#message-topic" >}}) to convey the detailed flow of messages between devices, between devices and components, or between components of an IoT solution. A message topic in this context should be thought of as a direct map to the pub/sub concept of a [subject](#) and as a similar concept to the partial URLs used to describe [request/response](#) and [REST](#) endpoints. By using a single concept to describe the subject of messages used in a design's flow, the IoT Atlas attempts to describe the concepts in the designs more simply.

Designs in the IoT Atlas will all assume that a device always has a solution unique `deviceId`. When every device has a solution unique ID, each specific example is more clear and an explicit list of devices can be used to implement a design in a way that supports multiple devices. When a list of devices is crucial to the design, it will be called out.   

Finally, each design will follow a few conventions. To convey an example of either data, or a code-related concept the `monospace` font will be used inline. When a word or concept is either crucial to the design or acting as a just-in-time definition a **bold** typeface will be used. When a block of code is best to convey or reinforce a concept, that block will be written at-least as pseudo-code. Over time we hope to have contributed and indexed examples of each design for a variety of languages and technologies.  

# Team
At this time, the core maintainers of the IoT Atlas are [Brett Francis](https://github.com/brettf), 
[Gavin Adams](https://github.com/gadams999), and 
[Craig Williams](https://github.com/typemismatch). We're excited to get these designs out in to the world so together we can accelerate IoT progress.   