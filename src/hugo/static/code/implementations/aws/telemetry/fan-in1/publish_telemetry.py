import base64
import json

print('Loading function')


def lambda_handler(event, context):
    output = []

    for record in event['records']:
        print(record['recordId'])
        payload = json.loads(base64.b64decode(record['data']).decode('utf-8'))

        transformedPayload = {}
        transformedPayload['deviceSerial'] = payload['deviceSerial']
        transformedPayload['timestamp'] = payload['timestamp']
        
        for data in payload['sensorData']:

            if data['sensorName'] == 'Temperature Celsius':
                transformedPayload['temperature'] = (data['sensorValue'] * 9/5) + 32  
            else:
                transformedPayload['temperature'] = data['sensorValue']

        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(json.dumps(transformedPayload).encode('utf-8'))
        }
        
        output.append(output_record)

    print('Successfully processed {} records.'.format(len(event['records'])))

    return {'records': output}    
