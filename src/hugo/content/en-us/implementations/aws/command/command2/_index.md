---
title: "Command - Device Shadow"
weight: 10
summary: "Command and control of a device using device shadow leveraging MQTT topics."
---

IOT Applications need a stable network to communicate with IoT devices in real time. However, in many IOT solutions where devices are deployed in far flung remote areas, remain disconnected to central application until required like when post of telemetry data is required or to get some updates from central solution. This can lead to synchronization and status issues that can impair IoT solution data collection and usage. Device shadow is a mechanism to address these connectivity and synchronization challenges by acting as a communication link between applications and IoT devices. Device Shadows provide a reliable data store for devices, apps, and other cloud services to share data. They enable devices, apps, and other cloud services to connect and disconnect without losing a device's state.


{{% notice note %}}
This implementation is designed using [AWS IOT device shadow service](https://docs.aws.amazon.com/iot/latest/developerguide/iot-device-shadows.html) via reserved MQTT shadow topics and focuses on two comparative use case implementation using device shadows.Please refer to the [Designing MQTT Topic for AWS IoT Core](https://docs.aws.amazon.com/whitepapers/latest/designing-mqtt-topics-aws-iot-core/designing-mqtt-topics-aws-iot-core.html), specifically the _Applications on AWS_ section. This white paper provides additional alternative patterns that go beyond the scope of this implementation.
{{% /notice %}}

## Use Cases

- Request or update device state configurations
  - _I want to track & control smart bulb from my mobile application_
  - _I want to remotely control household heater by turning them on/off or set to desired temperature_ 
- Request device actions based on some commands
  - _I want to remotely unlock door for a family visitor_ 
  - _I want to remotely instruct device to do some action on basis of a command_

## Reference Architecture

##### 1. Request or update device state configurations (using classic or unnamed shadow)

# ![Track and control device state configuration using shadow ](architecture1.svg)


- _AWS IoT Core_ is the MQTT message broker processing messages
- _Device_ is the IoT thing to be controlled
- _Application_ is the remote logic that issues commands, update device state configurations and consumes device telemetry data
- _Device Shadow_ is the replica which makes device's state available to applications and other services
- _ShadowTopicPrefix_ is an abbreviated form of the topic which can refer to either a named or an unnamed shadow, referred below for `$aws/things/device1/shadow` (classic shadow) used in above diagram.

1. The _Device_ establishes an MQTT connection to the _AWS IoT Core_ endpoint, and then subscribes to the reserved [MQTT shadow topics](https://docs.aws.amazon.com/iot/latest/developerguide/reserved-topics.html#reserved-topics-shadow)( e,g, `ShadowTopicPrefix/get/accepted`,`ShadowTopicPrefix/get/rejected`,  `ShadowTopicPrefix/update/accepted`,`ShadowTopicPrefix/update/rejected`,`ShadowTopicPrefix/update/delta`,  `ShadowTopicPrefix/update/documents`) (response) for device shadow it supports. These are the topics where shadow event messages will be received and processed. However, by using [ AWS IOT Device SDK ](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sdks.html) to call the Device Shadow service APIs, these topic subscriptions is automatically managed in background. The _Device_ publishes messages to `ShadowTopicPrefix/update`(request) topic. 
2. On successfull connect with _AWS IOT Core_ endpoint, the _Device_ publish request to  `ShadowTopicPrefix/get` topic and process latest shadow file received on `ShadowTopicPrefix/get/accepted` subscribed topic. After processing _desired_ state or configuration changes from shadow file, _Device_ makes publish request to `ShadowTopicPrefix/update` topic with device curent state as _reported_ data on shadow file.     
3. (Optional) Once the attributes are processed, and if device is persistently connected then it can subscribe to delta changes on shadow file to get further updates.  
4. The _Application_ establishes an MQTT connection to the _AWS IoT Core_ endpoint, and then publish _desired_ state changes on `ShadowTopicPrefix/update`(request) topic, also subscribed to the `ShadowTopicPrefix/update/accepted`,  `ShadowTopicPrefix/update/rejected` (response) topic to process telemetry data from device or sensors. 


{{% center %}}

```plantuml
@startuml
!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/InternetOfThings/all.puml
!includeurl AWSPuml/General/Client.puml

'Comment out to use default PlantUML sequence formatting
skinparam participant {
    BackgroundColor AWS_BG_COLOR
    BorderColor AWS_BORDER_COLOR
}
'Hide the bottom boxes
hide footbox

participant "<$IoTGeneric>\nDevice" as device
participant "<$IoTShadow>\nShadow" as shadow
participant "<$IoTCore>\nMQTT Broker" as broker
participant "<$Client>\nApplication" as app

== Connect and subscribe ==
device -> broker : connect(iot_endpoint)
broker -> shadow : reads current shadow file & delta 
device -> broker : subscribe("$aws/things/device1/shadow/get/accepted")
device -> broker : subscribe("$aws/things/device1/shadow/update/delta")
app -> broker : connect(iot_endpoint)
app -> broker : subscribe("$aws/things/device1/shadow/update/accepted")

== Command operation and (optional) response ==
app -> broker : publish("$aws/things/device1/shadow/update", "desired : {motorStatus: on}")
broker -> shadow : updates desired state on shadow file
device -> broker : publish("$aws/things/device1/shadow/update", "reported : {motorStatus: on}")
broker -> shadow : updates reported state on shadow file
broker -> app : publish("$aws/things/device1/shadow/update/accepted", "success")
app -> app : reconcile("device1")
@enduml
```

{{% /center %}}


##### 2. Request device actions based on some commands

![Command and control device action using shadow](architecture2.svg)

- _AWS IoT Core_ is the MQTT message broker processing messages
- _Device_ is the IoT thing to be controlled
- _Application_ is the remote logic that issues commands, update device state configurations and consumes device telemetry data
- _Device Shadow_ is the replica which makes device's state available to applications and other services
- _ShadowTopicPrefix_ is an abbreviated form of the topic which can refer to either a named or an unnamed shadow, referred below for `$aws/things/device1/shadow` (classic shadow) used in above diagram.

1. The _Device_ establishes an MQTT connection to the _AWS IoT Core_ endpoint, and then subscribes to the reserved [MQTT shadow topics](https://docs.aws.amazon.com/iot/latest/developerguide/reserved-topics.html#reserved-topics-shadow) for device shadow it supports. These are the topics where shadow event messages will be received and processed. The _Device_ publishes messages to `ShadowTopicPrefix/update`(request) topic.
2. On successfull connect with _AWS IOT Core_ endpoint, the _Device_ publish request to  `ShadowTopicPrefix/get` topic and process latest shadow file received on `ShadowTopicPrefix/get/accepted` subscribed topic. After processing _command_ from shadow file, _Device_ makes publish request to `cmd/device1/resp` (command action result) topic and also update command execution status on _reported_ state data on shadow file.     
3. (Optional) Once the command is processed, and if device is persistently connected then it can subscribe to delta changes on shadow file to get further command updates.  
4. The _Application_ establishes an MQTT connection to the _AWS IoT Core_ endpoint, and then publish command for device to act upon via _desired_ state changes on `ShadowTopicPrefix/update`(request) topic, also subscribed to the `ShadowTopicPrefix/update/accepted`,`ShadowTopicPrefix/update/rejected` and `cmd/device1/resp` (response) topic to process command action acknowledgement and  command action response respectively.
5. To send a command, the _Application_ publishes a message on the `ShadowTopicPrefix/update` topic by adding command request under desired state data for device. The _Application_ receives the command action response on 'cmd/device1/resp' topic and take appropriate action.
6. (Optional) Once the command has been processed, the device then publishes the result of the action onto the `cmd/device1/resp` topic. 
{{% center %}}

```plantuml
@startuml
!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/InternetOfThings/all.puml
!includeurl AWSPuml/General/Client.puml

'Comment out to use default PlantUML sequence formatting
skinparam participant {
    BackgroundColor AWS_BG_COLOR
    BorderColor AWS_BORDER_COLOR
}
'Hide the bottom boxes
hide footbox

participant "<$IoTGeneric>\nDevice" as device
participant "<$IoTShadow>\nShadow" as shadow
participant "<$IoTCore>\nMQTT Broker" as broker
participant "<$Client>\nApplication" as app

== Connect and subscribe ==
device -> broker : connect(iot_endpoint)
broker -> shadow : reads current shadow file & delta 
device -> broker : subscribe("$aws/things/device1/shadow/get/accepted")
device -> broker : subscribe("$aws/things/device1/shadow/update/delta")
app -> broker : connect(iot_endpoint)
app -> broker : subscribe("$aws/things/device1/shadow/update/accepted")
app -> broker : subscribe("cmd/device1/response")

== Command operation and (optional) response ==
app -> broker : publish("$aws/things/device1/shadow/update", "desired : {cmd: { action: start-motor, topic: cmd/device1/resp, ttl:3600 }")
broker -> shadow : updates desired state on shadow file
device -> broker : publish("$aws/things/device1/shadow/update", "reported : {cmd: {response: complete }")
broker -> shadow : updates reported state on shadow file
broker -> app : publish("$aws/things/device1/shadow/update/accepted", "success")
device -> broker : publish("cmd/device1/resp")
app -> app : reconcile("device1")

@enduml
```

{{% /center %}}

### Assumptions

This implementation approach has taken following assumptions-  
- The _Device_ is connected at all times, subscribed to a topic for incoming commands, and can receive and process the command. 
- The _Device_ can notify the sending _Application_ that the command was received and processed if needed.- All participants successfully receive, forward, and act up the message flows in either direction.
- Used classic shadow instead of named shadow.
- The _Device_ shadow is pre-created before device performs the get request on connect, otherwise shadow should be created first by publishing update with device current state.


## Implementation

Both the _Application_ and the _Device_ use similar approaches to connecting, sending, and receiving messages. The code samples below are complete for each participant.

{{% notice note %}}
The code samples focus on the _command_ design in general. Please refer to the [Getting started with AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html) for details on creating things, certificates, and obtaining your endpoint. The code samples below are used to demonstrate the basic capability of the _Command_ pattern.
{{% /notice %}}

### Device

The _Device_ code focuses on connecting to _Broker_ and then subscribing to reserved shadow topics to receive commands & configuration changes. Upon receipt of a command, the _Device_ performs some local action and then publishes the outcome (success, failure) of the command back to the _Application_, which then can reconcile the command.

The _Device_ will continue to receive and respond to commands until stopped.

{{< tabs groupId="device-code">}}
{{% tab name="python" %}}

Please refer to this [shadow sample](https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/shadow.py) for more details.

- Install SDK from PyPI: `python3 -m pip install awsiotsdk`
- Replace the global variables with valid endpoint, clientId, and credentials
- Start in a separate terminal session before running the _Application_: `python3 client.py`

```python
# client.py - Demonstrates waiting for a command or configuration updates for evaluation & processing

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient, AWSIoTMQTTClient
import json
import time
from random import randint

# This sample uses the AWS IoT Device Shadow Service to receive commands and also keep a property in 
# sync between device and server. On startup, the device requests the shadow document to learn 
# the property's initial state and process the attributes and commands passed in desired value of 
# shadow file. 
# The device also subscribes to "delta" events from the server,which are sent when a property's 
# "desired" value differs from its "reported" value.When the device learns of a new desired value,
# that data is processed on the device and an update is sent to the server with the new "reported" value.

# In this sample implementation an IOT edge device acting as actuator to switch on/off the motor 
# via shadow attribute.Additionally the device will action on command passed from server application
# on device shadow file.

# Using globals to simplify sample code

client_id = "REPLACE_WITH_DEVICE_ID"
client_token = "REPLACE_WITH_SECURE_DEVICE_TOKEN"
endpoint = "REPLACE_WITH_YOUR_ENDPOINT_FQDN"
client_certificate = "PATH_TO_CLIENT_CERTIFICATE_FILE"
client_private_key = "PATH_TO_CLIENT_PRIVATE_KEY_FILE"
root_ca = "PATH_TO_ROOT_CA_CERTIFICATE_FILE"
thing_name = "REPLACE_WITH_DEVICE_NAME"
motor_telemetry_topic = "REPLACE_WITH_TOPIC"

### Dummy state variables to showcase sample program logic and validation. 
## For actual implementation during device connect or reconnect, read this data as a last processed state from device store or via last reported state in shadow file.

DEVICE_MOTOR_STATUS = "off"
SHADOW_FILE_VERSION = 0


#Using the Shadow Client rather than the regular AWSIoTMQTTClient. 
# More details - https://s3.amazonaws.com/aws-iot-device-sdk-python-docs/sphinx/html/index.html#
# Similar functionality can be achieved by using AWSIOTMQTTClient also. 
# More details - https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/shadow.py

#Setup MQTT client and security certificates
#Make sure your certificate names match what you downloaded from AWS IoT

mqttShadowClient = AWSIoTMQTTShadowClient(thing_name)

#Use the endpoint from the settings page in the IoT console
mqttShadowClient.configureEndpoint(endpoint,8883)
# Thing certificate files goes here from AWS IOT
mqttShadowClient.configureCredentials(root_ca,client_private_key,client_certificate)

#Set up the Shadow handlers, setting up the persistent subscribe flag to true to get device updates
shadowClient=mqttShadowClient.createShadowHandlerWithName(thing_name,True)

#We can retrieve the underlying MQTT connection from the Shadow client to make regular MQTT publish/subscribe
mqttClient = mqttShadowClient.getMQTTConnection()

# Callback to update device shadow
def updateDeviceShadow(shadowMessage):
    global shadowClient
    print ("Updating reported state for shadow")
    print(shadowMessage)
    shadowMessage = json.dumps(shadowMessage)
    shadowClient.shadowUpdate(shadowMessage, customShadowCallback_Update, 5)

# Custom Shadow callback for update - checks if the update was successful.
def customShadowCallback_Update(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")
    if responseStatus == "accepted":
        print ("Reporting data state successfully updated in device shadow")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")
        
# Custom Shadow callback for delta payload
def customShadowCallback_Delta(payload, responseStatus, token):
    global DEVICE_MOTOR_STATUS
    global SHADOW_FILE_VERSION
    global thing_name
    global client_token
    processedAttrib = False
    processedCommand = False
    print ("Device Shadow delta update received")
    payloadDict = json.loads(payload)
    
    # Validation check for out of sequence or multiple deliveries of message
    if payloadDict.get("version") <= SHADOW_FILE_VERSION:
        print("Received shadow file version is old, skipping rest of the process")
        return
    
    # Validate client Token received
    if payloadDict.get("client_token") is not None:
        if payloadDict.get("client_token") != client_token:
            print("Invalid client token passed in delta update")
            return
    
    # validate if there is any update to device attributes
    if payloadDict["state"].get("deviceAttrib") is not None:
        DEVICE_MOTOR_STATUS = payloadDict["state"]["deviceAttrib"].get("motorStatus")
        print("Motor is turned - {}".format(DEVICE_MOTOR_STATUS))
        processedAttrib = True

    # Validate if there is any new command for device action, additional checks can be made on 
    # required keys existence
    if payloadDict["state"].get("command") is not None:
        value_ttl = payloadDict["state"]["command"].get("ttl")
        # Validate command validity based on the time to live (TTL) value
        if ((int(time.time()) - payloadDict.get("timestamp")) > value_ttl):
            print("Command validity expired, skipping action")
            return
        
        value_action = payloadDict["state"]["command"].get("action")
        ## Action type code block goes here
        if value_action == "relay-message":
            value_message = payloadDict["state"]["command"].get("message")
            value_topic = payloadDict["state"]["command"].get("topic")
            relay_message = {'msg':value_message, 'deviceId': thing_name}
            send(value_topic,mqttClient.json_encode(relay_message))
            processedCommand = True

    # Add code here to push latest processed shadow file version to local storage to pick during 
    # next reconnect for validations - store__to_local_storage(SHADOW_FILE_VERSION)
    if processedAttrib or processedCommand:
        # Update latest shadow file version
        SHADOW_FILE_VERSION = payloadDict["version"]
        
        print("Updated local shadow file version during delta callback")
    
    # For the purpose of demo, we are updating desired state from device, ideally modification of
    # desired state should be done by apps and reporting state by devices.
    # Update the shadow device file based on above processing as a response for sending application
    if processedAttrib and processedCommand:
        shadowMessage = {"state":{"desired":{"deviceAttrib":None,"command":None},"reported":{"deviceAttrib":{"motorStatus":DEVICE_MOTOR_STATUS},"command":{"action":"replay-message","response":"completed"}}}}
        updateDeviceShadow(shadowMessage)
    elif processedAttrib and not processedCommand:
        shadowMessage = {"state":{"desired":{"deviceAttrib":None},"reported":{"deviceAttrib":{"motorStatus":DEVICE_MOTOR_STATUS}}}}
        updateDeviceShadow(shadowMessage)
    else:
        shadowMessage = {"state":{"desired":{"command":None},"reported":{"command":{"action":"replay-message","response":"completed"}}}}
        updateDeviceShadow(shadowMessage)

    return

        
#Callback function to encode a payload into JSON
def json_encode(string):
        return json.dumps(string)

mqttClient.json_encode=json_encode

#Callback function to publish data on MQTT topics
def send(topicname,message):
    mqttClient.publish(topicname, message, 1)
    print("Message published on topic - '{}'.".format(topicname))

        

# Callback function for shadow GET request on initial connect or reconnect 
def on_initial_connect_or_reconnect(response, responseStatus, token):
    global SHADOW_FILE_VERSION
    global DEVICE_MOTOR_STATUS
    global thing_name
    global client_token
    processedAttrib = False
    processedCommand = False
    print("Fetched latest shadow file")
    payloadDict = json.loads(response)
    
    
    try:
        # Validate response status
        if (responseStatus != 'accepted'):
            print("Not able to get shadow file for device, please create device shadow first. Or add shadow code here by publishing to /update Topic")
            return
        # Validate last processed shadow file version
        if (payloadDict.get("version") != None and payloadDict.get("version")) <= SHADOW_FILE_VERSION:
                print("No new data to process, skipping get shadow document processing!")
                return
        # Validate client token
        if payloadDict.get("client_token") != None:
            if payloadDict["client_token"] != client_token:
                print("Invalid client token passed")
                return
            
        if payloadDict["state"].get("delta") is not None:
                
                # Update latest shadow file version
                SHADOW_FILE_VERSION = payloadDict.get("version")
                # Push latest processed shadow file version to local storage to pick during 
                # next reconnect for validations - store__to_local_storage(SHADOW_FILE_VERSION)
                print("Updated local shadow file version after connect")
                
                # Check for any device attribute changes 
                if payloadDict["state"]["delta"].get("deviceAttrib") is not None:
                    DEVICE_MOTOR_STATUS = payloadDict["state"]["delta"]["deviceAttrib"].get("motorStatus")
                    print("Motor is turned - {}".format(DEVICE_MOTOR_STATUS))
                    processedAttrib = True
                        
                # Check if any command passed for device action
                if payloadDict["state"]["delta"].get("command") is not None:
                    value_ttl = payloadDict["state"]["delta"]["command"].get("ttl")
                    print (int(time.time()))
                    print (payloadDict.get("timestamp"))
                    # Validate command validity based on TTL
                    if ((int(time.time()) - payloadDict.get("timestamp")) > value_ttl):
                        print("Command validity expired, skipping action")
                        return
                    else:
                        # Action to perform on device for completing the command
                        
                        print("Executing command action..")
                        value_action = payloadDict["state"]["delta"]["command"].get("action")
                        if value_action == "relay-message":
                            value_message = payloadDict["state"]["delta"]["command"].get("message")
                            relay_message = {'msg':value_message,"deviceId": thing_name}
                            value_topic = payloadDict["state"]["delta"]["command"].get("topic")
                            send(value_topic,mqttClient.json_encode(relay_message))
                            processedCommand = True
                
                # Update the shadow device file based on above processing as a response for sending application
                if processedAttrib and processedCommand:
                    shadowMessage = {"state":{"desired":{"deviceAttrib":None,"command":None},"reported":{"deviceAttrib":{"motorStatus":DEVICE_MOTOR_STATUS},"command":{"action":"replay-message","response":"completed"}}}}
                    updateDeviceShadow(shadowMessage)
                elif processedAttrib and not processedCommand:
                    shadowMessage = {"state":{"desired":{"deviceAttrib":None},"reported":{"deviceAttrib":{"motorStatus":DEVICE_MOTOR_STATUS}}}}
                    updateDeviceShadow(shadowMessage)
                else:
                    shadowMessage = {"state":{"desired":{"command":None},"reported":{"command":{"action":"replay-message","response":"completed"}}}}
                    updateDeviceShadow(shadowMessage)
        
        
    except Exception as e:
        exit(e)
        
def on_get_shadow_rejected(error):
    
    try:
        if error.code == 404:
            exit("No shadow document found")
        else:
            exit("Get request was rejected. code:{} message:'{}'".format(
                error.code, error.message))

    except Exception as e:
        exit(e)


def on_update_shadow_rejected(error):
    try:
        exit("Update request was rejected. code:{} message:'{}'".format(
            error.code, error.message))

    except Exception as e:
        exit(e)

def exit(msg_or_exception):
    print("Exiting sample:", msg_or_exception)
    mqttShadowClient.disconnect()

            
#Connect to the IOT Core MQTT broker
mqttShadowClient.connect()
print ("Connected")

# Read last processed shadow file version
# SHADOW_FILE_VERSION = read__from_local_storage()

# Device can only have one unnamed or classic shadow but can have multiple named shadows
# Get the latest state from the Device shadow on initial connect
shadowClient.shadowGet(on_initial_connect_or_reconnect, 5)


print("registered for delta callback")
# Listen for delta changes, when device is connected to IOT Core MQTT broker
shadowClient.shadowRegisterDeltaCallback(customShadowCallback_Delta)


try:
    ## Publish Motor telemetry data when in on state
    while True:
        vibration = randint(-500, 500)
        if DEVICE_MOTOR_STATUS == "on":
            relay_message = {'vibration':vibration, 'deviceId': thing_name}
            send(motor_telemetry_topic,mqttClient.json_encode(relay_message))
            print("Motor vibration data pushed")
            time.sleep(5)
except KeyboardInterrupt:
    print("disconnecting")
    mqttShadowClient.disconnect()
```

- Update shadow request document 

```json

{
  "state": {
    "desired": {
      "deviceAttrib" :{
      		"motorStatus" : "off"
      },
      "command":{
      		"action":"relay-message",
      		"message": "Message sent as part of command action",
      		"topic":"cmd/device1/response",
      		"ttl":300
      }
    },
    "reported": {
      "deviceData" :{
      		"motorStatus" : "off"
      }
    }
  },
  "clientToken":"myapp123"
}

```

{{% /tab %}}
{{< /tabs >}}

### Application

The _Application_ code connects to the Broker and subscribes to the _Device_'s response topic. It then waits for a command to be entered and sends that to the _Device_'s request topic.

This implementation uses AWS CLI to demonstrate how an app can interact with a shadow.

- To get the current state of the shadow using the AWS CLI. From the command line, enter this command.

```cmd

aws iot-data get-thing-shadow --thing-name REPLACE_WITH_DEVICE_NAME  /dev/stdout

```

- To update a shadow from an app

```cmd


aws iot-data update-thing-shadow --thing-name REPACE_WITH_DEVICE_NAME \
    --cli-binary-format raw-in-base64-out \
    --payload ''{"state":{"desired":{"deviceAttrib":{"motorStatus":"on"},"command":{"action":"relay-message","message":"Message sent as part of command action","topic":"cmd/REPLACE_WITH_DEVICE_NAME/resp","ttl":300}}},"clientToken":"myapp123"}'' /dev/stdout

```


## Considerations

This implementation covers the basics of a command and control pattern. It does not cover certain aspects that may arise in production use.