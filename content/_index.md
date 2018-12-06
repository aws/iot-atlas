---
title: "Home"
---
{{< atlas-logo >}} 
# Welcome
# 欢迎 

Welcome to the IoT Atlas, where successful journeys using the internet of things rely on maps.

欢迎来到IoT Atlas，成功使用物联网的旅程依赖于地图。

The most successful Internet of Things (aka IoT) projects have clearly defined business outcomes. The vast majority of IoT projects traverse different phases, starting from prototype, through pilot and limited production toward production, to achieve the identified business outcome at scale. The IoT Atlas supports your project by explaining the why, what, and who of commonly used, modern IoT designs.

最成功的物联网（又名IoT）项目明确定义了业务成果。绝大多数物联网项目都经历了不同阶段，从原型，试点和有限生产​​到生产，从而实现规模化的业务成果。IoT Atlas 通过解释常用的现代物联网设计的原因，内容和人员来支持您的项目。

## Overview
## 概览
Many IoT designs now being used globally are well-worn and time-tested but not widely known. The designs often come from mature domains such as *sensor networks*, *[control system](https://en.wikipedia.org/wiki/Control_system)* architectures, *[machine-to-machine ](https://en.wikipedia.org/wiki/Machine_to_machine)* networks, and *[embedded system](https://en.wikipedia.org/wiki/Embedded_system)* development. But the lack of visibility of those mature designs is causing many people to [reinvent the wheel](https://en.wikipedia.org/wiki/Reinventing_the_wheel) for their solution, when they'd prefer not. Further complicating the matter for experienced practitioners, even when a long-standing design is known, the design often needs to be revised to take into account cloud development concepts. 

目前全球范围内使用的许多物联网设计都被广泛使用并久经考验，但却并不为人熟知。这些设计通常来自成熟领域，如 *传感器网络*，*[控制系统架构](https://en.wikipedia.org/wiki/Control_system)*，*[机器对机器网络](https://en.wikipedia.org/wiki/Machine_to_machine)* 和 *[嵌入式系统开发](https://en.wikipedia.org/wiki/Embedded_system)*。但是那些成熟设计并不为人所熟知，导致许多人不得不重新发明轮子以解决问题。对于经验丰富的从业者来说，这个问题进一步复杂化，即使是由来已久的设计，通常也需要进行修改以便考虑到云开发的概念。

The IoT Atlas is an educational resource for both new and long-time practitioners of internet of things solutions. It updates and expands upon well-worn designs with the presumption that today, building "Internet of Things" solutions almost always means that "a hyper-scale cloud is available" to practitioners building each solution. Taking the stance that solutions development can rely upon the existence of a hyper-scale cloud does not imply the IoT Atlas' designs must be connected in order to operate. Instead the designs attempt to leverage the strength of a fleet of devices operating locally in remote environments for long periods of time **and** the cloud's strengths of massive scale, global ubiquity, and solution agility. The designs can then be used to build bar-raising solutions that expect intermittent, long-duration, or primarily-disconnected network outages as a fundamental influence of their designed components. Essentially the designs herein follow the IoT philosophy that *the edge completes the cloud*. 

IoT Atlas是面向物联网解决方案全新和经验丰富从业者提供的教育资源。它更新并扩展了广泛使用的设计，并假设在今天构建“物联网”解决方案几乎总是意味着构建每个解决方案的从业者都可以使用“超大规模的云”。解决方案的开发依赖于超大规模云并不意味着IoT Atlas的设计必须连接到云端才能运行。相反，这些设计试图同时利用到长时间在远程环境中本地运行的设备群的优势**和**云的大规模，遍布全球和解决方案敏捷性的优势。这些设计可用于构建高质量的解决方案，并把网络间歇性、长时间和经常中断对其设计组件的影响考虑在内。事实上，这里的设计遵循IoT理念：*边缘使云完整(the edge completes the cloud)*。
 
By starting from this perspective, we are creating an atlas that supports an understanding of even the most complex IoT considerations. It would be great to have you join us and [contribute](https://github.com/aws/iot-atlas/blob/master/CONTRIBUTING.md) your ideas for designs, considerations, and examples to this journey. 

从这个角度出发，我们正在创建一个地图集以便支持我们去理解即使是最复杂的物联网设计的注意事项。 如果您加入我们并[贡献](https://github.com/aws/iot-atlas/blob/master/CONTRIBUTING.md)您的设计理念、注意事项和示例，这将是非常棒的事情。


## Organization
## 组织

Each design attempts to cover one concept, cover it well, and, when it makes sense, describe how the current design will interoperate with other designs. When a new concept is necessary to better understand a design, the concept will be introduced just in time in the design and also referenced in the [glossary]({{< ref "/glossary" >}}). 

每个设计都试图涵盖一个概念并深入阐述，并在有需要时，描述当前设计如何与其他设计进行互操作。 当有需要一个新的概念来更好地理解设计时，该概念将在设计中被及时引入，并在[词汇表]（{{<ref“/ glossary”>}}）中引用。
 
To meet the bar for publication, a fully-formed IoT Atlas design will provide a simple one or two sentence description, a concise description of the IoT challenge the design addresses, a simple non-vendor-specific architectural diagram and process flow, the personae commonly interested in and impacted by the capabilities delivered by the design, and key implementation considerations. The key considerations of a design are to be documented in the IoT Atlas itself and also through links to papers that provide additional context; such as, white-papers, blog posts, and generally any vetted content on the internet which best conveys what should be considered.  

为了满足发布的要求，IoT Atlas中一个完整的设计将提供简单的一两句话描述
、针对该设计所需要应对的物联网挑战的简明描述、简单的不针对某个厂商的架构图和流程、对设计感兴趣并受交付结果所影响的人，以及实施的关键考虑因素。设计的关键考虑因素应被记录在IoT Atlas中，并提供链接到相关资料，包括白皮书、博客以及互联网上其他经过审查的相关内容。

## Design Considerations
## 设计的考虑因素
  
#### Level of Abstraction
#### 抽象级别

Each design attempts to describe the pattern at a level of abstraction that incorporates as many details as possible, but no more than necessary. Of course this is a hard balance to achieve and will surely adjust over the lifetime of this effort. 



Initially the IoT Atlas will describe designs just **above** the details of which communication protocol, which vendor, or which programming language might be used in an implementation. For example, the [Telemetry](/designs/telemetry) design is purposefully described just above the details of [CoAP](http://coap.technology/), [MQTT](http://mqtt.org/), or [AMQP](https://www.amqp.org/product/architecture) and yet someone familiar with these protocols would still understand the design's concept without any or only a slight amount of transformation. This position is taken because the designs should benefit as many people as possible regardless of tooling and vendor-specific implementation details. However, vendor-specific Examples can accelerate understanding for those starting out. As such the IoT Atlas will accept Example reference implementations of Designs which are more specific than pseudo-code can achieve.
 
It is unlikely that all possible perspectives can be incorporated, but the goal of describing designs at this level of abstraction is in line with the primary intent to help practitioners understand the design across the widest possible set of IoT solutions.

#### Key Concepts
Designs in the IoT Atlas will use the concept of [message topics]({{< ref "/glossary#message-topic" >}}) to convey the detailed flow of messages between devices, between devices and components, or between components of an IoT solution. A message topic in this context should be thought of as a direct map to the pub/sub concept of a [subject](#) and as a similar concept to the partial URLs used to describe [request/response](#) and [REST](#) endpoints. By using a single concept to describe the subject of messages used in a design's flow, the IoT Atlas attempts to describe the concepts in the designs more simply.

Designs in the IoT Atlas will all assume that a device always has a solution unique `deviceID`. When every device has a solution unique ID, each specific example is more clear and an explicit list of devices can be used to implement a design in a way that supports multiple devices. When a list of devices is crucial to the design, it will be called out.   

#### Conventions
Finally, each design will follow a few conventions. To convey an example of either data, or a code-related concept the `monospace` font will be used inline. When a word or concept is either crucial to the design or acting as a just-in-time definition a **bold** typeface will be used. When a block of code is best to convey or reinforce a concept, that block will be written at-least as monospaced `pseudo-code`. Over time we hope to have contributed and indexed examples of each design for a variety of languages and technologies.  

## Team
At this time, the core maintainers of the IoT Atlas are [Brett Francis](https://github.com/brettf), 
[Gavin Adams](https://github.com/gadams999), and 
[Craig Williams](https://github.com/typemismatch). We're excited to get these designs out into the world so together we can accelerate IoT progress with you.   
