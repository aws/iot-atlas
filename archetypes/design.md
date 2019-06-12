---
title: {{ .Name }}
date: {{ .Date }}
weight: 99
draft: true
type: 'design'
layout: 'single'
---
<!-- TODO author a new synopsis in /layouts/shortcodes/ and update the line below -->
{{< synopsis-command >}}
<!--more-->

## Challenge

** REPLACE ME: summary of design's challenge **

## Solution

** REPLACE ME: summary of design's solution. Add a png of your design and update the pptx **

The {{ .Name }} design shown in the following diagram can deliver this functionality.

![{{ .Name }} Design](command.png) ([PPTx](/designs/iot-atlas-patterns.pptx))

### Diagram Steps

** REPLACE ME: summary of design's challenge **

1. A [device]({{< ref "/glossary/vocabulary#device" >}}) configures itself to communicate with a protocol endpoint so that Command messages can be sent and received.
2. A component of the solution publishes a [Command message]({{< ref "/glossary/vocabulary#command-message" >}}) targeted at one or more devices.
3. The server uses the protocol endpoint to send the Command message to each previously configured device.
4. Upon completion of the Command's requested action, the device publishes a command completion message to the server via the protocol endpoint.

## Considerations

** REPLACE ME: summary of considerations **

When implementing this design, consider the following questions:

#### REPLACE ME SAMPLE SUBHEADER QUESTION

** REPLACE ME SAMPLE ANSWER **

## Examples

### REPLACE ME SAMPLE EXAMPLE
** REPLACE ME SAMPLE EXPLANATION **

#### REPLACE ME SAMPLE EXAMPLE SUBSECTION
** REPLACE ME SAMPLE EXPLANATION SUBSECTION **