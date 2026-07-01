import json
import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import urllib.request

def lambda_handler(event, context):
    dynamodb_client = boto3.resource('dynamodb', region_name=os.environ['region'])
    iot_client = boto3.client('iot', region_name=os.environ['region'])

    try:
        device_uid = event['device_uid']
        device_token = event['device_token']
    except Exception:
        return prepare_result(event, "ERROR", 500, {"message": "Missing input data"})
        
    print("Device registration request for {}".format(device_uid))
    
    dynamodb_table = dynamodb_client.Table(os.environ['device_dynamodb_table'])
    
    try:
        device_info = dynamodb_table.query(
            KeyConditionExpression="device_uid = :a",
            ExpressionAttributeValues={
                ":a": device_uid
            }
        )
    except ClientError:
        return prepare_result(event, "ERROR", 500, {"message": "Device database access error"})
        
    if len(device_info['Items']) <= 0:
        return prepare_result(event, "ERROR", 404, {"message": "Device not found"})
    else:
        if device_info['Items'][0]['is_registered'] == 1:
            return prepare_result(event, "ERROR", 500, {"message": "Device is already registered"})
        if device_info['Items'][0]['is_enabled'] == 0:
            return prepare_result(event, "ERROR", 500, {"message": "Device isn't enabled"})
        if device_info['Items'][0]['device_token'] != device_token:
            return prepare_result(event, "ERROR", 500, {"message": "Device token is not valid"})

    print("Database checks passed for {}, the next is create_keys_and_certificate()".format(device_uid))
    
    certificate = iot_client.create_keys_and_certificate(setAsActive=True)
    if not certificate:
        return prepare_result(event, "ERROR", 500, {"message": "Unable to create device certificates"})

    print("Database checks passed for {}, the next is attach_policy()".format(device_uid))
    
    try:
        iot_client.attach_policy(policyName=os.environ['iot_policy_name'], target=certificate['certificateArn'])
    except:
        return prepare_result(event, "ERROR", 500, {"message": "Unable to attach policy to the certificate"})

    try:
        time_registered = datetime.now().isoformat()
        attribute_payload = {
            "attributes": {
                'device_uid': device_uid,
                'registered_via': "iot-core-cvm",
                'registered_on': time_registered
            },
            "merge": True
        }
        
        thing_name = os.environ['thing_name_format'].replace("%DEVICE_UID%", "{}").format(device_uid)
        thing = iot_client.create_thing(thingName=thing_name, attributePayload=attribute_payload)
    except:
        return prepare_result(event, "ERROR", 500, {"message": "Unable to create thing"})
        
    try:
        iot_client.attach_thing_principal(principal=certificate['certificateArn'], thingName=thing_name)
    except:
        return prepare_result(event, "ERROR", 500, {"message": "Unable to attach certificate to the device"})


    root_certificate_request = urllib.request.urlopen(os.environ['iot_root_ca_url'])
    if root_certificate_request.getcode() != 200:
        return prepare_result(event, "ERROR", 500, {"message": "Unable to download root CA"})
    
    root_certificate = root_certificate_request.read()
    
    try:
        device_info_update = dynamodb_table.update_item(
            Key={"device_uid": device_uid},
            UpdateExpression="set iot_core_thing_name = :t, iot_core_registered_on = :o, is_registered = :r ",
            ExpressionAttributeValues={
                ":t": thing_name,
                ":o": time_registered,
                ":r": 1
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError:
        return prepare_result(event, "ERROR", 500, {"message": "Database error during device record update"})
        
    if 'Attributes' not in device_info_update:
        return prepare_result(event, "ERROR", 500, {"message": "Device info couldnt updated."})
    
    try:
        iot_core_endpoint = iot_client.describe_endpoint(
            endpointType='iot:Data-ATS'
        )
    except:
        return prepare_result(event, "ERROR", 500, {"message": "Error while getting IoT Core endpoint"})
        
    if not "endpointAddress" in iot_core_endpoint:
        return prepare_result(event, "ERROR", 500, {"message": "Invalid IoT Core endpoint response"})

    payload = {
        "endpoint": iot_core_endpoint["endpointAddress"],
        "thing_name": thing_name,
        "certificates": {
            "device_certificate": certificate['certificatePem'],
            "root_ca": root_certificate
        },
        "keyPair": {
            "publicKey": certificate['keyPair']['PublicKey'],
            "privateKey": certificate['keyPair']['PrivateKey']
        }
    }

    return prepare_result(event, "SUCCESS", 200, payload)


def prepare_result(event, result_type, status_code=200, payload=None):

    result = {
        'statusCode': status_code,
        'status':result_type
    }
    
    if payload:
        result["payload"] = payload
    
    print("Invocation for EVENT='{}', finished with STATUS='{}', STATUS_CODE='{}'".format(
            json.dumps(event), 
            result_type, 
            status_code)
        )
    
    return result

