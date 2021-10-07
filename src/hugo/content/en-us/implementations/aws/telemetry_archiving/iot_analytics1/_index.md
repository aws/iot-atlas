---
title: "Iot Analytics - ETL"
weight: 10
summary: "Archival and ETL of Telemetry Data using AWS IoT Analytics"
---

ETL of IoT telemetry data is the process that transforms and prepares telemetry data for analytics, reporting, and archival. An _AWS IoT Analytics Pipeline_ can filter, select attributes, remove attributes, apply math functions, enrich device data or state and apply custom Lambda logic to data. 

## Use Cases

<!--
#TODO come up with use case for both ETL and cold storage, divvy up the below references as applicable

https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/databases.html
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/failure-management.html
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/review.html
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/cost-effective-resources.html
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/analytics.html
-->

- Archive
    - _I need to near real time archive sensor transmitted to AWS IoT Core with SQL queries over the MQTT broker_
    - _I need to bulk archive sensor data from a SCADA historian or other data store_
- Transform Data
    - _I need to transform sensor data, but I don't have specialized ETL developer skills or an ETL tool_ 
    - _I need to rapidly iterate on ETL transformations on sensor data_
    - _I need to experiment and compare different ETL transformation on the same sensor data_
    - _I need to reprocess data sets I've already ingested and processed with new or updated transformations_
- Analyze 
    - _I need to easily perform analysis on sensor data without setting up a BI tool or a DataLake_
    - _I need to make transformed sensor data readily available for analysis in a BI tool or to an AI/ML notebook_


## Reference Architecture

- _Devices_ are the IoT things transmitting telemetry
- _AWS IoT Core_ is the MQTT message broker processing messages on behalf of the clients and uses a Rule Action to put messages onto a Channel. 
- _SCADA Historian_ is an on premises data storage of device data.
- _Amazon Kinesis_ is a streaming target for historian data migration.
- _Amazon Lambda_ runs a serverless function to process stream data from Kinesis and batch put it onto a Channel.
- _AWS IoT Analytics_ comprises of 
  - _IoT Analytics Channel_ where raw messages are stored for a period of time. Devices can send data to multiple Channels.
  - _IoT Analytics Pipeline_ that performs ETL activities on messages consumed from a channel.
  - _IoT Analytics Datastore_ is where a Pipeline writes data.
  - _IoT Analytics Dataset_ is a materialized view over a Datastore that can optionally be delivered to S3.
- _Amazon QuickSight_ is the BI tool where you create and publish analytics dashboards.
- _Jupyter_ is the analytics workflow notebook you containerize to perform analysis over your SQL Dataset.
- _Amazon S3_ is the storage sink for IoT Analytics and allows data to be stored securely as well as accessed by other processes or consumed as part of your DataLake.

![ETL via IoT Analytics](architecture.svg)

{{< tabs groupId="analytics" align="center" >}}
{{% tab name="1a. MQTT Real Time" %}}

1. _Devices_ establish an MQTT connection to the _AWS IoT Core_ endpoint, and then publish message to the `dt/plant1/dev_n/temp` (data telemetry) topic. This is a location and device specific topic to deliver telemetry messages for a given device or sensor.
1. A Topic Rules publishes the results of a wildcard SQL `dt/plant1/+/temp` from the MQTT Broker then puts messages onto the _IoT Channel_ which stores that data in an S3 bucket for a set period of time.
1. The _IoT Analytics Pipeline_ executes a workflow of activities including reading from the Channel, performing filtering and transformations, and writing to the Datastore.
1. The _IoT Analytics Datastore_ makes transformed data available to source Datasets.
1. The _IoT Analytics Dataset_ is a materialized view defined in SQL over a Datastore, multiple Datasets can be created over a single Datastore. 
1. _Amazon QuickSight_ reads from a Dataset and displays visualizations and dashboards.
1. _Jupyter_ notebooks .
1. _S3 DataLake_ stores Channel, Datastore and optionally Dataset data.

```plantuml
@startuml
!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/InternetOfThings/all.puml
!includeurl AWSPuml/Analytics/QuickSight.puml
!includeurl AWSPuml/Storage/SimpleStorageServiceS3.puml

'Comment out to use default PlantUML sequence formatting
skinparam participant {
    BackgroundColor AWS_BG_COLOR
    BorderColor AWS_BORDER_COLOR
}
'Hide the bottom boxes
hide footbox

participant "<$IoTGeneric>\nDevices" as devices
participant "<$IoTCore>\nMQTT Broker" as broker
participant "<$IoTRule>\nRule" as rule
participant "<$IoTAnalyticsChannel>\nChannel" as channel
participant "<$IoTAnalyticsPipeline>\nPipeline" as pipeline
participant "<$IoTAnalyticsDataStore>\nDataStore" as datastore
participant "<$QuickSight>\nQuickSight" as quicksight
participant "<$SimpleStorageServiceS3>\nS3 Bucket" as bucket

== Publish, Archive, Transform, and Store ==
devices -> broker : connect(iot_endpoint)
devices -> broker : publish("dt/d_1/aggregate")
devices -> broker : publish("dt/d_2/aggregate")
devices -> broker : publish("dt/d_n/aggregate")
broker <- rule : select * from \n'dt/+/aggregate'
rule -> channel : batchPutMessage(\n\tmessages)'

channel <- pipeline : p1.read(raw_data)
pipeline -> datastore: p1.put(xformed_data)
channel <- pipeline : p2.read(raw_data)
pipeline -> datastore: p2.put(xformed_data)
channel <- pipeline : p3.read(raw_data)
pipeline -> datastore: p3.put(xformed_data)
datastore <- quicksight: read
channel -> bucket: put(raw_data)
pipeline -> bucket: put(xformed_data)

@enduml
```

{{% /tab %}}
{{% tab name="1b. SCADA Historian"  %}}

1. _DMS_ reads data from a historian database and puts it onto an _Amazon Kinesis Data Stream_. A _Lambda_ function then reads data from Kinesis using the SDK and uses IoT Analytics Channel batchPutMessage to put data onto the _IoT Analytics Channel_. This pattern demonstrates how IoT Analytics makes the same ETL and analysis flows available for near real time and batch. 
1. A Topic Rules publishes the results of a wildcard SQL `dt/plant1/+/temp` from the MQTT Broker then puts messages onto the _IoT Channel_ which stores that data in an S3 bucket for a set period of time.
1. The _IoT Analytics Pipeline_ executes a workflow of activities including reading from the Channel, performing filtering and transformations, and writing to the Datastore.
1. The _IoT Analytics Datastore_ makes transformed data available to source Datasets.
1. The _IoT Analytics Dataset_ is a materialized view defined in SQL over a Datastore, multiple Datasets can be created over a single Datastore. 
1. _Amazon QuickSight_ reads from a Dataset and displays visualizations and dashboards.
1. _Jupyter_ notebooks .
1. _S3 DataLake_ stores Channel, Datastore and optionally Dataset data.

```plantuml
@startuml
!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/InternetOfThings/all.puml
!includeurl AWSPuml/Analytics/Kinesis.puml
!includeurl AWSPuml/Database/all.puml
!includeurl AWSPuml/Analytics/QuickSight.puml
!includeurl AWSPuml/Storage/SimpleStorageServiceS3.puml
!includeurl AWSPuml/Compute/Lambda.puml

'Comment out to use default PlantUML sequence formatting
skinparam participant {
    BackgroundColor AWS_BG_COLOR
    BorderColor AWS_BORDER_COLOR
}
'Hide the bottom boxes
hide footbox

participant "<$Database>\nSCADA" as historian
participant "<$DatabaseMigrationService>\nDMS" as dms
participant "<$Kinesis>\nKinesis" as stream
participant "<$Lambda>\nLambda" as lambda
participant "<$IoTAnalyticsChannel>\nChannel" as channel
participant "<$IoTAnalyticsPipeline>\nPipeline" as pipeline
participant "<$IoTAnalyticsDataStore>\nDataStore" as datastore
participant "<$QuickSight>\nQuickSight" as quicksight
participant "<$SimpleStorageServiceS3>\nS3 Bucket" as bucket

== Batch, Archive, Transform, and Store ==
historian <- dms : read(data)
dms -> stream : put(data)
stream <- lambda : read(data)
lambda -> channel : batchPutMessage(\n\tmessages)'

channel <- pipeline : p1.read(raw_data)
pipeline -> datastore: p1.put(xformed_data)
datastore <- quicksight: read
channel -> bucket: put(raw_data)
pipeline -> bucket: put(xformed_data)

@enduml
```

{{% /tab %}}
{{< /tabs >}}


## Implementation

In this implementation you'll setup an IoT Analytics implementation and then use a python script to simulate devices publishing messages to your AWS IoT Core endpoint. Upon deployment into production you’ll configure multiple devices as AWS IoT Things that each securely communicate with a Gateway and or your AWS IoT Core endpoint.

{{% notice note %}}
The processing flow for path **1a** is covered in the implementation below. Flow **1b** has the same processing flow as **1a** for step 2 and beyond once data is put  onto the Channel. In flow **1b** bulk data is sourced from a SCADA historian database and is pushed into the _IoT Analytics Channel_ using [BatchPutMessage](https://docs.aws.amazon.com/iotanalytics/latest/APIReference/API_BatchPutMessage.html) by a Lambda function after DMS replicates data to Kinesis. Refer to the aws blog titled [Injecting data into AWS IoT Analytics from a Kinesis Data Stream](https://aws.amazon.com/blogs/iot/injecting-data-into-aws-iot-analytics-from-amazon-kinesis-data-streams/) to consume Kinesis data with a Lambda. Refer to  [AWS DMS with a Kinesis target](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Kinesis.html) to read data from a historian database and write to Kinesis. 
{{% /notice %}}

<!--
#ToDO good reference for IOT analytics CLI commands -> https://aws.amazon.com/blogs/iot/collecting-organizing-monitoring-and-analyzing-industrial-data-at-scale-using-aws-iot-sitewise-part-3/

https://aws.amazon.com/blogs/iot/data-ingestion-using-aws-step-functions-aws-iot-events-and-aws-iot-analytics/

https://aws.amazon.com/blogs/iot/injecting-data-into-aws-iot-analytics-from-amazon-kinesis-data-streams/ 
-->

### Assumptions

This implementation assumes that you are comfortable using the AWS CLI. If you've not installed the AWS CLI, follow the  [installation of the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) instructions. The implementation also assumes you  using the default AWS CLI profile or you've set the corresponding session based shell variables [AWS_PROFILE](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html) and [AWS_DEFAULT_REGION](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html). Otherwise, if you are using a named profile be sure to either the `---profile <profile-name> and --region <aws-region>` arguments to your CLI commands.

## IoT Analytics Channel

First establish a Channel for Analytics Data. The Channel can be stored in an AWS or customer managed bucket, in this case we'll default to AWS managed. The storage retention can be indefinite or based on time in years and days, in this case we'll default to indefinite. 

```yaml
aws iotanalytics create-channel --channel-name etl_device_data
```

## Iot Core Topic Rule

An IoT Core Topic Rule will batch put messages into a channel as they are published to the MQTT Broker. You'll need to create an IAM role with a trust relationship for iot.amazon.com and permission to BatchPutMessage(s) to IoT Analytics and optionally to write logs to CloudWatch if logging is enabled in your IoT Core settings. 

First create a policy allowing IoT Core to assume the EtlAnalyticsRole so that it can write to your Channel. 
```yaml
aws iam create-role --role-name EtlAnalyticsRole --assume-role-policy-document file://policy_assume_role.json
```
Save the below JSON to a file named policy_assume_role.json before executing the command above.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "iot.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

Next create and attach a policy to your EtlAnalyticsRole giving your Topic Rule the needed permissions.
```yaml
aws iam put-role-policy --role-name EtlAnalyticsRole --policy-name EtlAnalyticsPolicy --policy-document file://policy_etl_analytics.json
```
Save the below JSON to a file named policy_etl_analytics.json. Be sure to replace `<REGION>` with your region and `<ACCOUNT-ID>` with your account id before you execute the command above.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "iotanalytics:BatchPutMessage",
            "Resource": [
               "arn:aws:iotanalytics:<REGION>:<ACCOUNT-ID>:channel/etl_device_data"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:<REGION>:<ACCOUNT-ID>:log-group:/aws/iotanalytics/pipeline:*"
            ]
        }
    ]
}
```

To enable logging for IoT Core execute the following command, be sure to replace `<ACCOUNT-ID>` with your account id before you execute the command. This step is optional.
```yaml
aws iot set-logging-options --logging-options-payload roleArn=arn:aws:iam::<ACCOUNT-ID>:role/EtlAnalyticsRole,logLevel=INFO
```

Now you can create the topic rule.  
```yaml
aws iot create-topic-rule --rule-name etl_analytics --topic-rule-payload file://topic_rule.json
```
Save the JSON below to a file named topic_rule.json. Be sure to `<ACCOUNT-ID>` with your account id before executing the command above. 
```json
{
    "sql": "SELECT * FROM 'dt/+/aggregate'",
    "ruleDisabled": false,
    "awsIotSqlVersion": "2016-03-23",
    "actions": [
        {
            "iotAnalytics": {
                "channelName": "etl_device_data",
                "roleArn": "arn:aws:iam::<ACCOUNT-ID>:role/EtlAnalyticsRole"
            }
        }
    ],
    "errorAction": {
        "cloudwatchLogs": {
            "roleArn": "arn:aws:iam::<ACCOUNT-ID>:role/EtlAnalyticsRole",
            "logGroupName": "/aws/iot-rules/etl_data"
        }
    }
}
```

## IoT Analytics Datastore

The IoT Analytics Datastore is a storage location for transformed data after the Pipeline workflow performs ETL. The Datastore stores data in S3 either in an AWS or customer managed bucket, for simplicity this implementation uses an AWS managed bucket. Like a Channel storage is indefinite or time based in years and days, we will use the default of indefinite in this case. A Datastore also must choose a data format of JSON or Parquet with a schema definition, this cannot be changed after creation. In this case we'll use Parquet with a defined schema. Execute the command below to create your Datastore.

```yaml
aws iotanalytics create-datastore --cli-input-json file://datastore.json
```
Save the JSON below to a file name datastore.json before executing the command above.
```JSON
{
    "datastoreName": "etl_aggregate_store",
    "datastoreStorage": {
        "serviceManagedS3": {}
    },
    "retentionPeriod": {
        "unlimited": true
    },
    "fileFormatConfiguration": {
        "parquetConfiguration": {
            "schemaDefinition": {
                "columns": [
                    {
                        "name": "device_id",
                        "type": "string"
                    },
                    {
                        "name": "temperature",
                        "type": "int"
                    },
                    {
                        "name": "temperature_fahrenheit",
                        "type": "int"
                    },
                    {
                        "name": "humidity",
                        "type": "int"
                    },
                    {
                        "name": "timestamp",
                        "type": "string"
                    }
                ]
            }
        }
    },
    "datastorePartitions": {
        "partitions": [
            {
                "timestampPartition": {
                    "attributeName": "timestamp",
                    "timestampFormat": "yyyy-MM-dd HH:mm:ss"
                }
            }
        ]
    }
}
```

## IoT Analytics Pipeline

The IoT Analytics Pipeline can contain a number of activities in an ETL workflow. The first activity is required, reading from a Channel. The last activity is also required, writing to a Datastore. Between these you can add a number of activities needed for your data. We'll perform a simple math equation converting Celsius to Fahrenheit. Execute the command below to create the Pipeline. 

```yaml
aws iotanalytics create-pipeline --cli-input-json file://pipeline.json
```
Save the JSON below to a file named pipeline.json before executing the command above.
```JSON
{
    "pipelineName": "calculate_fahrenheit",
    "pipelineActivities": [
        {
            "channel": {
                "name": "2",
                "channelName": "etl_device_data",
                "next": "calculate_fahrenheit_activity"
            }
        },
        {
            "math": {
                "name": "calculate_fahrenheit_activity",
                "attribute": "temperature_fahrenheit",
                "math": "(temperature * 9/5) + 32 ",
                "next": "3"
            }
        },
        {
            "datastore": {
                "name": "3",
                "datastoreName": "etl_aggregate_store"
            }
        }
    ]
}
```

## Device Simulation

Our IoT Analytics environment is setup and our Pipeline is ready to perform ETL on incoming data. For this implementation we'll run a few threads to simulate devices and generate data. Feel free to analyze the code and modify the device and publishing settings but be aware that you cannot use a sensor count greater than the number of threads the computer you run this on has available. Be sure to replace `<IOT-CORE-ENDPOINT>` with your IoT Core endpoint. You can see your endpoint on the IoT Core service page under Settings, Device Data Endpoint. You can also retrieve the endpoint via the CLI by running the command below. 

```yaml
aws iot describe-endpoint
```
Ensure you have python 3 installed on your machine. Then execute the command below.
```yaml
python data_generator.py
```

Before running the command above, save the python code below to a file named data_generator.py
```python
#!/usr/bin/env python3

import random
import time
import boto3
import json
from multiprocessing import Pool
from datetime import datetime


iot_client = boto3.client(
    "iot-data", endpoint_url="<IOT-CORE-ENDPOINT>"
)


def read(sensor):
    message = {}
    message["device_id"] = f"sensor{sensor}"
    message["temperature"] = random.randrange(45, 92, 2)
    message["humidity"] = random.randrange(0, 100, 2)
    message["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(message)

    topic = f"dt/{message['device_id']}/aggregate"
    iot_client.publish(topic=topic, payload=json.dumps(message))


if __name__ == "__main__":
    sensor_count = 10  # maps to physical threads on your machine
    seconds_between_publishing = 10
    publishes = 50

    with Pool(sensor_count) as p:
        for _ in range(publishes):
            p.map(read, range(sensor_count))
            time.sleep(seconds_between_publishing)

```

## IoT Analytics Dataset

```yaml
aws iotanalytics create-dataset --cli-input-json file://dataset.json
```

```JSON
{
    "datasetName": "etl_aggregate_data",
    "actions": [
        {
            "actionName": "onetime_action",
            "queryAction": {
                "sqlQuery": "select * from etl_aggregate_store"
            }
        }
    ]
}
```

### Considerations

pipelines noisy data - blank values, varying schema. can filter messages

data from sitewise as a source to the channel

enriching data from the shadow or device registry

using customer managed vs aws managed buckets


### Cleanup

```yaml
aws iam delete-role-policy --role-name EtlAnalyticsRole --policy-name EtlAnalyticsPolicy
aws iam delete-role --role-name EtlAnalyticsRole
aws iot delete-topic-rule --rule-name onetime_analytics

aws iotanalytics delete-channel --channel-name etl_device_data

aws iotanalytics delete-dataset --dataset-name etl_aggregate_data
```