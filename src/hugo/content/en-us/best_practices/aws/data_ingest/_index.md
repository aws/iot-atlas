---
title: "AWS IoT Data Ingest Best Practices"
weight: 50
author: felerp@amazon.com
summary: "Best practices for data ingest with AWS IoT"
---



## Welcome

A key feature of any IoT application is the collection of data from a fleet of devices, and being able to process and analyze that data in the cloud.  **Ingest** - where the data is received from the devices, and sent for processing - is a critical stage in this workflow.  When designing your application with AWS IoT, there are several factors and methods to consider regarding the ingest of your device data, and they may present different tradeoffs. 

By following some best practices, you can ensure that your application’s ingestion layer is more closely aligned with your specific business needs, and with the pillars of the [**AWS Well-Architected Framework**](https://aws.amazon.com/architecture/well-architected): Cost Optimization, Performance Efficiency, Reliability, Security, and Operational Excellence.

In the sections below, best practices are organized by pillar.  However, please note that some best practices have impact across multiple.  For optimal results, you should evaluate your IoT application from the perspective of all five pillars.

* [Cost Optimization](#cost)  
* [Performance Efficiency](#performance)   
* [Reliability](#reliability)     
* [Security](#security)  
* [Operational Excellence](#operational)

Additional ingest-related considerations and recommendations can be found in the [Appendix section](#appendix).

<a name="cost"></a>

-----
## Cost Optimization Considerations:

#### Leverage local processing to aggregate, batch, filter, or compress message payloads at the Edge for greater efficiency

**Local or Edge processing** refers to work that we can do on our IoT hardware devices to facilitate more efficient data ingestion to the cloud.  There are different ways this can be leveraged, and depends on your needs, and the capabilities and constraints of your hardware and network.


Some key questions to consider:

*How often does your application require messages (data) to be sent from devices?  Does it require a constant stream of small messages (for frequent telemetry or updates)?  Or can you batch messages for a certain interval (for example, minutes/hours) before sending?*  


* This will inform the frequency of your device’s messages back to the cloud.  Where periodic messages back to cloud are suitable, your device can combine multiple smaller messages into batches for greater transmission efficiency. See [About Message Size](#messagesize) below.

*Is there business value to transmitting all data from your devices to the cloud?  Or are you able to summarize data, remove duplicate values, truncate, or ignore certain categories in order to transmit less data overall?*  

* This will inform whether you can take steps to reduce the quantity of messages, and the corresponding payload size, which can save on messaging, and downstream storage and processing costs.  Local processing can be leveraged to perform these operations. For example, consider whether you can safely ignore certain events entirely.  In such cases, your device can filter out those events to avoid incurring the costs of transmitting and processing them.
* If you are able to reduce the number of decimal places/precision of values, or abbreviate certain text values to make them shorter, you can achieve a smaller message size/byte count.
* In situations where telemetry data must be sent, _do you need to include all of the raw data?_  For example, you can leverage local processing to aggregate or average data values, and just send the summarized results back to the cloud instead.

You can also use serialization frameworks to compress the message payload. <b>Caveat</b>: this is best suited for use cases where IoT Rules do not need to directly inspect the payload of the message, as it will be unreadable in its encoded state.

<a name="messagesize"></a>
##### About Message Size: 

AWS IoT Core messages are metered in 5KB increments, with a maximum message size of 128KB.
For example, a 2KB message has the same cost as a 5KB message, and a 6KB message has the same cost as a 10KB message.

Assuming your devices are not hardware constrained, for optimal efficiency, try to keep message size to the nearest 5KB, and consider batching several smaller messages (<5KB) into a larger one.

**Caveat:** Balance batch size against the delay of transmission, and the risk of losing a message containing multiple batched events, to your application.

<br>

{{% notice note %}}
Certain optimizations can add complexity and delays to message processing, which should be carefully evaluated against any cost savings benefits.
{{% /notice %}}


##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-20-4.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-21-2.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/optimizing-over-time.html  

<br>

#### Use IoT Core’s Basic Ingest to save on messaging costs

[AWS IoT Core pricing](https://aws.amazon.com/iot-core/pricing) is based on a few different components.

**Basic Ingest** allows you to send incoming device data directly to other AWS services via IoT rule actions, without incurring the IoT Core messaging costs. Other IoT Core cost components will still apply.  

Basic Ingest helps optimize high-volume data ingestion by bypassing the publish/subscribe message broker within AWS IoT Core, and sending the data directly to pre-defined IoT rules associated with Basic Ingest reserved topics (use a $ prefix).

**Caveat:** Other devices and rules cannot subscribe to these topics.  If multiple subscribers are a requirement, use a standard topic instead.

Your devices can use a combination of standard and Basic Ingest topics, as needed, to achieve the best blend for cost optimization.

For example, if your use case involves incoming device data going directly to [specific AWS services](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rule-actions.html) such as DynamoDB, Kinesis, S3, IoT Analytics, or Lambda, you can leverage Basic Ingest to achieve greater cost savings.

##### Learn more: 
https://docs.aws.amazon.com/iot/latest/developerguide/iot-basic-ingest.html  
https://docs.aws.amazon.com/iot/latest/developerguide/iot-rule-actions.html  
https://docs.aws.amazon.com/whitepapers/latest/designing-mqtt-topics-aws-iot-core/mqtt-design-best-practices.html

<br>

#### Or, send high-volume telemetry data direct to a buffering service

In high-volume telemetry and video scenarios, it can be more cost effective to bypass AWS IoT Core for ingest, and send your incoming device data directly to a buffer/stream like Amazon Kinesis Data Streams, or Amazon Kinesis Video Streams, while separately maintaining fleet command and control via AWS IoT Core.

**Caveat:** You can’t use AWS IoT Core’s rules engine on the data ingested this way, and would need to implement your own logic using other means - such as with AWS Lambda functions.


<a name="cost_datalake"></a>
#### Use a data lake for ingested data

A [**data lake**](https://aws.amazon.com/big-data/datalakes-and-analytics/what-is-a-data-lake) is a centralized repository that allows you to store all of your structured and unstructured data at any scale. Typically built around Amazon S3, the data lake is flexible, can be extended with other purpose-built stores to accommodate vast amounts and varieties of data, and serves as a source for analytics.

For each IoT telemetry use case, select a data format and data store which cost-effectively matches the data’s characteristics, intended usage patterns, and lifecycle requirements.

Depending on your use case, IoT data can be ingested through AWS IoT Core and sent to Amazon S3 using IoT rules, or landed via other means, such as Amazon Kinesis Data Firehose, or having IoT devices write batched data directly to Amazon S3. 

As data ages, manage its lifecycle in accordance with your organization’s data retention policies. For example, tools such as [S3 Lifecycle policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html) or [S3 Intelligent Tiering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering-overview.html) can help automate the movement of data to more cost-effective infrequent access and archive tiers

Rather than building your own solution, you can also leverage managed services such as [AWS IoT Analytics](https://aws.amazon.com/iot-analytics). It collects, pre-processes, enriches, stores, and analyzes IoT device data that you send to it. 

##### Learn more:
https://aws.amazon.com/big-data/datalakes-and-analytics/what-is-a-data-lake  
https://aws.amazon.com/big-data/datalakes-and-analytics/data-lake-house/  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-20-1.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/design-principle-22.html  
https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering-overview.html  
https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html  

<br>

#### Batch incoming data using IoT Core rules, before sending downstream to other AWS Services
Once ingested, putting telemetry data into batches allows those batches to be processed or stored in bulk, which can be more efficient.

For example, you can batch telemetry message data with Amazon Kinesis Data Firehose, before writing to Amazon S3 in bulk.  Writing fewer, larger files of device telemetry data to S3 is more efficient than writing numerous smaller files.  In this example, writing and reading many small files will incur increased S3 costs for PUT and GET operations.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/cost-effective-resources.html

<a name="performance"></a>

-----

## Performance Efficiency Considerations:

#### Balance the frequency and amount of data sent from your devices with your application’s needs, and your device’s hardware and network constraints

Consider how often your application requires messages (data) to be sent from devices.  *Does it require a constant stream of small messages (i.e. frequent updates)?  Or does your use case support batching messages for a certain interval before sending?*

* Balance this against your device’s limitations.  IoT devices may have limited processing power/local storage/battery power, and be connecting over intermittent or slow network connections.  Hence, it may be impractical to connect too frequently (e.g. drains battery), and yet, there may also be a need to connect frequently enough to not lose device data (e.g. local storage gets full, and overwritten).  

* This will inform the frequency of your device’s messages back to the cloud.  If your application does not require immediate updates from your devices, consider sending less frequently to conserve network bandwidth and battery power.

You should also consider whether there is business value to transmitting all raw data from your devices to the cloud.  *Are you able to summarize data, remove duplicate values, truncate, or ignore certain categories in order to transmit less data overall?*

* This will inform whether you can take local processing steps to reduce the quantity of messages, and the corresponding payload sizes, which can be helpful with constrained networks.   

If your hardware and use case supports it:
* Determine what data needs to be transmitted in the first place - perhaps there are only a few categories that have value, and you can filter out the rest.
* Consider compressing payloads and batching events into a single message before sending to the cloud, for greater transmission efficiency.
* Perform local processing to aggregate data points, and send the results, as opposed to the raw data.

These considerations are also important from a [cost optimization](#cost) lens.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/tradeoffs.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-19-3.html

<br>

#### If using MQTT protocol, determine the optimal Quality of Service (QoS) level for publishing messages

AWS IoT Core supports MQTT Quality of Service (QoS) levels 0 and 1.

QoS level 0 will send a message 0 or more times, and hence delivery is not guaranteed.  It is the suggested default in cases where connections are considered generally reliable, and when missing messages are not a problem for the IoT application.

QoS level 1 will send a message at least once, and repeatedly until acknowledged.  It should be used in situations where at-least-once delivery is required.  Tradeoffs for the reliability include added overhead, latency, and potential for duplicate messages.

Also see: [Connection Methods Overview](#appendix) in the Appendix.

##### Learn more:
https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-19-2.html

<br>

#### For applications requiring immediate processing of device telemetry, process data offline at the Edge

In situations where a device is not hardware constrained, but network connectivity is, edge solutions such as AWS IoT Greengrass can be used to locally process data and respond to events sooner.

For example, in an industrial use case, local processing can more quickly detect and respond to particular equipment events or conditions, as opposed to waiting for data to be sent to the cloud, processed remotely, and an alert raised from there. 

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/tradeoffs.html


<a name="perf_localgateway"></a>
#### Consider having constrained local devices interface with a local gateway

If you have a group of highly-constrained local devices (e.g. sensors with limited local storage, or WAN connectivity) and installed in a particular place (e.g. a factory), a local gateway can act as a storage location, aggregator, and intermediary to the cloud. 

A local gateway can store, batch, manipulate, enrich, and process data from other local devices, before sending relevant data to the cloud on their behalf.  Examples include using AWS IoT Greengrass, or AWS IoT SiteWise in industrial equipment use cases.  

Processing (or pre-processing) data on a local gateway can result in faster responses to events, and reduced processing and compute requirements for that data, once delivered to the cloud.   

##### Learn more: 
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-15-3.html

<br>

#### Use managed services to reduce your undifferentiated heavy lifting

Managed services remove manual effort, maintenance burden, and reduce complexity.  Leveraging them within your ingest pipeline and IoT application will assist in improving performance, scalability, and reliability.
 
##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/selection.html

<br>

#### Decouple ingest from processing with queues and streams 

Implementing **loose coupling** between AWS IoT Core and downstream services will help avoid overwhelming your application if ingest volumes and rates are higher than current processing capacity, and facilitates the scaling of your IoT application.

Use IoT rules to send data to buffer and streaming services like Amazon SQS, Amazon Kinesis, and Amazon Managed Streaming for Apache Kafka (MSK).  These services will hold the data safely, until a downstream application can process them.  

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/ingestion-layer.html  
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-workload-architecture.html (See REL4)

<br>

#### Batch incoming data using IoT rules, before sending downstream to other AWS Services

Once received, putting telemetry data into batches allows those batches to be processed or stored in bulk, which can be more efficient.

For example, you can batch telemetry message data with Amazon Kinesis Data Firehose, before writing to Amazon S3 in bulk.  Writing fewer, larger objects of device telemetry data to S3 is more efficient than writing numerous smaller ones.  Furthermore:
* If any transformations or conversions to the data are required, they could be more efficiently applied to the batch, before being persisted.  
* Having many small objects in S3 can inflate the number of objects in your buckets.

More generally, batching data can also help to avoid potential performance bottlenecks or [service quotas](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html) with downstream AWS services, for example, with AWS Lambda concurrency.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/cost-effective-resources.html  
https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html

<br>

#### Monitor your IoT application for performance and to detect potential issues

Continuously monitor your application to evaluate its performance and detect indications of potential interruption.  

For example, ensure that it is not hitting or approaching any AWS [service quotas](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html) as you scale .  Where service quotas do exist, dive deeper to understand which are adjustable (soft limits), and which are not (hard limits).

Apply tools such as Amazon CloudWatch to determine the baseline patterns, metrics, and KPIs for your application.  Continue to monitor and track those metrics, and set alarms to notify you as required.   

This practice applies across multiple pillars, including Performance Efficiency, Reliability, and Operational Excellence.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-18-1.html  
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-foundations.html  
https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-23-3.html  

<br>

#### Test!

Stage production-scale testing to ensure your entire IoT application, including the ingest layer, continues to work and scale as expected, as the load increases.

You can use a simulator application to generate events at the appropriate scale.

During testing, closely watch relevant performance metrics, including those that relate to any [service quotas](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html).

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/design-principle-16.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-16-4.html  
https://docs.aws.amazon.com/iot/latest/developerguide/device-advisor.html  

<a name="reliability"></a>

-----
## Reliability Considerations:

#### Design devices for failures and intermittent connectivity

IoT devices may have limited battery power, and be connecting over intermittent or poor network connections.  Hence, devices may be offline for long periods of time.  

To ensure that your IoT application can ultimately ingest the data from your devices, you will need to design them to tolerate intermittent connectivity.  Do this by storing important data locally until connectivity is restored, while respecting hardware (storage and power) constraints.  For example, AWS SDKs and AWS IoT Greengrass support local buffering of data to disk while devices are disconnected.

As mentioned in [the Performance pillar](#perf_localgateway), you can also leverage a local gateway to augment highly-constrained devices.  A local gateway can store, batch, manipulate, enrich, and process data from other local devices, before sending relevant data to the cloud on their behalf.  For example, using AWS IoT Greengrass, or AWS IoT SiteWise in industrial equipment use cases.

For situations where devices are experiencing difficulties connecting to the cloud, implement retry logic and use randomization and exponential back-off to ensure that your fleet of devices stagger the timing of their connections, so they don’t all try to connect at once and generating a preventable spike in traffic. 

For added resiliency, consider supporting multiple cloud connection methods (e.g. cellular, wi-fi), and failing-over to a backup method when necessary to send critical messages.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-11-2.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-11-4.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-15-3.html  

<br>

#### Decouple ingest from processing with queues and streams 

Implementing **loose coupling** between AWS IoT Core and downstream services will help prevent data loss in case downstream services are not responding.  Additionally, this design will avoid overwhelming your application if ingest volumes and rates are higher than current processing capacity, and facilitates the scaling of your IoT application.

Use IoT rules to send data to buffer and streaming services like Amazon SQS, Amazon Kinesis, and Amazon Managed Streaming for Apache Kafka (MSK).  These services will hold the data safely, until a downstream application can process them.  

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/ingestion-layer.html  
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-workload-architecture.html (See REL4)

<br>

#### Save ingested data to durable storage before processing

Saving incoming device data to durable storage (e.g. Amazon S3) before processing provides a backup copy in case of errors.  It also provides the option for processing the raw data differently in the future, if your needs change.

For example, during ingest, an AWS IoT rule can send device data to Amazon Kinesis Data Firehose, which can batch the data and deliver it to Amazon S3.  If you choose to apply transformations to the data through Kinesis Firehose, you also have the option of persisting the raw data in its original format to another S3 location, giving you an unmodified source backup.
 
Depending on your use case, there are many other durable storage options that you can use - including Amazon EBS (if processing with Amazon EC2 resources), or database services such as Amazon DynamoDB, Amazon Timestream, or Amazon Aurora, to name a few.
 
If required, consider copying critical data to another location (AWS Region or Availability Zone, as appropriate) for disaster recovery purposes.

Also see: [Use a data lake](#cost_datalake) in the cost section above.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-10-1.html

<br>

#### Use Error Actions for your IoT rules

If an AWS IoT rule action experiences a problem - for example, a downstream service doesn't accept data from IoT Core, you can configure **error actions** to mitigate.  Error actions are defined within IoT rules, and only occur if an IoT rule action fails. 

You can leverage them to generate alerts and prevent data loss during a failure.  For example, you can send an alert via a SNS topic, and save the device data to an alternate durable location (such as S3, SQS, Kinesis) for analysis or future retry.  Ensure your error action does not write to the same service as the rule’s primary action, to avoid having the same issue disrupt the error action (for example, if a service quota was hit).

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/failure-management.html  
https://docs.aws.amazon.com/iot/latest/developerguide/rule-error-handling.html

<br>

#### Monitor your IoT application for performance and to detect potential issues

Continuously monitor your application to evaluate its performance and detect indications of potential interruption.  

For example, ensure that it is not hitting or approaching any AWS [service quotas](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html) as you scale. Where service quotas do exist, dive deeper to understand which are adjustable (soft limits), and which are not (hard limits).

Apply tools such as Amazon CloudWatch to determine the baseline patterns, metrics, and KPIs for your application.  Continue to monitor and track those metrics, and set alarms to notify you as required.   

This practice applies across multiple pillars, including Performance Efficiency, Reliability, and Operational Excellence.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-18-1.html  
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-foundations.html  
https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-23-3.html  


<a name="security"></a>

----
## Security Considerations:

#### Assign each device a unique identity and X.509 certificate

It is essential that trust is established between your IoT devices and your IoT application.

Your IoT devices should each be given a unique identity in AWS IoT, backed by a unique, trusted X.509 certificate.  Certificates should not be shared.  This allows for fine-grained access management.  

In the event of device compromise or retirement, revocation of the specific device’s certificate would allow targeted blocking of the affected device.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-1-1.html

<br>

#### Enforce least privilege access for MQTT topics

To reduce risk, enforce least privilege access to your MQTT topics.

Create granular IoT permissions (i.e. policies) that only allow devices and applications to access the specific MQTT topics they require.  For example, each device can be given access to its own MQTT topic, but not those of others.  Meanwhile, your application may have different requirements, and may require access to the topics of many devices in order to perform its work.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-1-2.html



<a name="operational"></a>

----
## Operational Excellence Considerations:

#### Monitor your IoT application for performance and to detect potential issues

Continuously monitor your application to evaluate its performance and detect indications of potential interruption.  

For example, ensure that it is not hitting or approaching any AWS [service quotas](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html) as you scale.  Where service quotas do exist, dive deeper to understand which are adjustable (soft limits), and which are not (hard limits).

Apply tools such as Amazon CloudWatch to determine the baseline patterns, metrics, and KPIs for your application.  Continue to monitor and track those metrics, and set alarms to notify you as required.   


This practice applies across multiple pillars, including Performance Efficiency, Reliability, and Operational Excellence.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-18-1.html  
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-foundations.html  
https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-23-3.html  

<br>

#### Configure detailed logging for enhanced troubleshooting and operational insights

You can enable logging in AWS IoT to capture more information about messages as they arrive from devices, pass through the MQTT broker, and the rules engine.  This can be very helpful for troubleshooting purposes during ingest, or for proactively detecting emerging issues that could impact application health.

Logs are sent to Amazon CloudWatch logs.

Log verbosity level is adjustable.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-23-3.html  
https://docs.aws.amazon.com/iot/latest/developerguide/configure-logging.html  
https://docs.aws.amazon.com/iot/latest/developerguide/cloud-watch-logs.html  



<a name="appendix"></a>

-----
## Appendix: Additional ingest-related considerations and recommendations

<br>

### Connection Methods Overview - Selecting the right approach:  

Connect your devices to AWS IoT Core using the most appropriate method for your use case:

<table>
  <tr>
    <th>Pick</th>
    <th>Description</th>
    <th>When</th>
	<th>Comments</th>
  </tr>
  <tr>
    <td>AWS IoT Core with MQTT</td>
    <td>Use AWS IoT Core for data ingest and device management capabilities, with MQTT protocol</td>
    <td>Your devices support MQTT</td>
	<td>
		<ul>
			<li>Supports long-lived connections</li>
			<li>Publish and subscribe</li>
			<li>Rules engine</li>
			<li>MQTT QoS levels 0 and 1 supported</li>
		</ul>
	</td>
  </tr>
  <tr>
    <td>AWS IoT Core with HTTPS</td>
    <td>Use AWS IoT Core for data ingest with HTTPS protocol</td>
    <td>Your devices do not support MQTT, or preference for HTTPS</td>
	<td>
		<ul>
			<li>Connections are not long-lived (polling)</li>
			<li>Publish capabilities only (no subscribe)</li>
			<li>Rules engine</li>
		</ul>
	</td>
  </tr>
  <tr>
    <td>Hybrid</td>
    <td>Devices connect to AWS IoT Core for management, but data ingested by other means</td>
    <td>You are ingesting large data payloads that exceed 128KB (and cannot be split up) - such as video</td>
	<td>
		<ul>
			<li>Manage and control device fleet via AWS IoT Core (using MQTT)</li>
			<li>Data ingest done via other means e.g. Amazon Kinesis Video Streams, Amazon Kinesis Data Streams, Amazon MSK, Amazon SQS, or Amazon API Gateway</li>
		</ul>
	</td>
  </tr>
   <tr>
    <td>Custom solution</td>
    <td>Connect devices and ingest data using a fully-custom solution (not AWS IoT)</td>
    <td>You are running a proprietary or legacy solution that does not rely on AWS IoT</td>
	<td>
		<ul>
			<li>Self-managed IoT devices</li>
			<li>AWS IoT Core is not used</li>
			<li>Could ingest data via custom application (e.g. running on Amazon EC2), or other AWS services (e.g. Amazon Kinesis, Amazon MSK, Amazon SQS, or Amazon API Gateway)</li>
		</ul>
	</td>
  </tr>
   <tr>
    <td>IoT Core with MQTT over Websockets</td>
    <td>Use AWS IoT Core for data ingest and device management capabilities, with MQTT protocol over WebSockets connections</td>
    <td>Your devices already use, or there is a preference for WebSockets</td>
	<td>
		<ul>
			<li>Same MQTT functionality, over long-lived WebSockets connections</li>
		</ul>
	</td>
  </tr>
</table>


##### Learn more:
https://docs.aws.amazon.com/iot/latest/developerguide/protocols.html

<br>

### Miscellaneous Edge Considerations

#### Maintain accurate device time in Universal Time (UTC)

Accurate device time is important for data capture timestamps, and security purposes (e.g. evaluating validity of certificates, and hence authentication).  However, batteries of IoT devices may discharge, and clocks may drift over time.  As a result, consider having your devices synchronize their time with an accurate external source, such as a NTP server, where possible.

By standardizing on Universal Time (UTC) for your devices, you can ensure consistency across your fleet, regardless of physical location.  This abstracts away time zones or adjustments for Daylight savings time at the device level.

##### Learn more:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-12-1.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-16-3.html

<br>

#### Use unique device IDs for your IoT devices, and include the ID with the data payload

Beyond the [security value](#security) of having a unique ID for each device, this ensures the source of the data can be easily identified, and facilitates enrichment of the data with other information that is already stored or known about the device.

<br>

#### Edge devices should generate a sequential event ID to serialize each event

While time stamps are useful to order data collected or generated by IoT devices, it is possible that multiple items could end up with the same time stamp.  Assigning a sequential event ID to each event will help determine the correct order. 

<br>

### Additional Resources:

IoT Lens - AWS Well-Architected Framework:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/welcome.html

IoT Lens Checklist:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/overview.html

AWS Well-Architected Framework:
https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html

AWS IoT Core Developer Guide:
https://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html








