---
title: "Home"
---

{{< atlas-logo-bad >}}

Welcome to the IoT Atlas, where successful journeys using the Internet of Things (IoT) rely on maps.

The most successful IoT projects have clearly defined business outcomes. The vast majority of IoT projects traverse different phases, starting from prototype, through pilot and limited production toward production, to achieve the identified business outcome at scale. The IoT Atlas supports your project by explaining the why, what, and who of commonly used, modern IoT designs.

## Overview

Many IoT designs now being used globally are well-worn and time-tested but not widely known. The designs often come from mature domains such as _sensor networks_, _[control system](https://en.wikipedia.org/wiki/Control_system)_ architectures, _[machine-to-machine ](https://en.wikipedia.org/wiki/Machine_to_machine)_ networks, and _[embedded system](https://en.wikipedia.org/wiki/Embedded_system)_ development. But the lack of visibility of those mature designs is causing many people to [reinvent the wheel](https://en.wikipedia.org/wiki/Reinventing_the_wheel) for their solution, when they would prefer not. Further complicating the matter for experienced practitioners, even when a long-standing design is known, the design often needs to be revised to take into account cloud development concepts.

The IoT Atlas is a resource for both new and long-time builders of internet of things solutions. It updates and expands upon well-worn designs with the presumption that today, building "Internet of Things" solutions almost always means that "a hyper-scale cloud is available" to practitioners building each solution. Taking the stance that solutions development can rely upon the existence of a hyper-scale cloud does not imply the IoT Atlas' designs must be connected in order to operate. Instead the designs attempt to leverage the strength of a fleet of devices operating locally in remote environments for long periods of time **and** the cloud's strengths of massive scale, global ubiquity, and solution agility. The designs can then be used to build bar-raising solutions that expect intermittent, long-duration, or primarily-disconnected network outages as a fundamental influence of their designed components. Essentially the designs herein follow the IoT philosophy that _the edge completes the cloud_.

By starting from this perspective, we are creating an atlas that supports an understanding of even the most complex IoT considerations. It would be great to have you join us and [contribute](https://github.com/aws/iot-atlas/blob/main/CONTRIBUTING.md) your ideas for designs, considerations, and examples to this journey.

## Organization

Each design attempts to cover one concept, cover it well, and, when it makes sense, describe how the current design will interoperate with other designs. When a new concept is necessary to better understand a design, the concept will be introduced just in time in the design and also referenced in the [glossary]({{< ref "/glossary" >}}).

To meet the bar for publication, a fully-formed IoT Atlas design will provide a simple one- or two-sentence description, a concise description of the addressed IoT challenge, a simple non-vendor-specific architectural diagram and process flow, the personae commonly interested in and impacted by the capabilities delivered by the design, and key implementation considerations. The key considerations of a design will be documented in the IoT Atlas itself and also through links to resources that provide additional context, such as white-papers, blog posts, and vetted content on the Internet that best conveys what should be considered.

## Design Considerations

#### Level of Abstraction

Each design attempts to describe the pattern at a level of abstraction that incorporates as many details as possible, but no more than necessary. Of course, this is a hard balance to achieve and will surely be adjusted over the lifetime of this effort.

Initially, the IoT Atlas will describe designs just **above** the details of which communication protocol, which vendor, or which programming language might be used in an implementation. For example, the [Telemetry]({{< ref "/patterns/telemetry" >}}) design is purposefully described just above the details of [CoAP](http://coap.technology/), [MQTT](http://mqtt.org/), or [AMQP](https://www.amqp.org/product/architecture) and yet someone familiar with these protocols would still understand the design's concept without any or with only a slight amount of transformation. This position is taken because the designs should benefit as many people as possible regardless of tooling and vendor-specific implementation details. However, vendor-specific examples can accelerate understanding for those starting out. As such, the IoT Atlas will accept reference implementations of designs, which are more specific than pseudo-code can achieve.

It is unlikely that all possible perspectives can be incorporated, but the goal of describing designs at this level of abstraction is in line with the primary intent to help practitioners understand the design across the widest possible set of IoT solutions.

#### Key Concepts

Designs in the IoT Atlas will use the concept of [message topics]({{< ref "/glossary/vocabulary#message-topic" >}}) to convey the detailed flow of messages between devices, between devices and components, or between components of an IoT solution. A message topic in this context should be thought of as a direct map to the pub/sub concept of a [subject](#) and as a similar concept to the partial URLs used to describe [request/response](#) and [REST](#) endpoints. By using a single concept to describe the subject of messages used in a design's flow, the IoT Atlas attempts to describe the design concepts in a simpler way.

Designs in the IoT Atlas will all assume that a device always has a solution-unique `deviceID`. When every device has a solution-unique ID, each specific example is more clear and an explicit list of devices can be used to implement a design in a way that supports multiple devices. When a list of devices is crucial to the design, it will be called out.

#### Conventions

Finally, each design will follow a few conventions. To convey an example of either data or a code-related concept, the `monospace` font will be used inline; when a word or concept is either crucial to the design or acting as a just-in-time definition, a **bold** typeface will be used; when a block of code is best to convey or reinforce a concept, that block will be written at-least as monospaced `pseudo-code`. Over time, we hope to contribute and index examples of each design for a variety of languages and technologies.

## Team

At this time, the core maintainers of the IoT Atlas are [Brett Francis](https://github.com/brettf),
[Gavin Adams](https://github.com/gadams999), and
[Craig Williams](https://github.com/typemismatch). We're excited to get these designs out into the world here and on [GitHub](https://github.com/aws/iot-atlas); so together we can accelerate IoT progress with you.
