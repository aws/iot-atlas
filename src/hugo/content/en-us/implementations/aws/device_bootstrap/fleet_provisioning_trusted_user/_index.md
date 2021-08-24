---
title: "Fleet Provisioning - Trusted User"
weight: 10
summary: "Bootstraping device provisioning using Cognito authenticated user and Provisioning template"
---

AWS IoT provides an application programming interface (API) that allows mobile/web applications to generate temporary certificates and private keys. The device leaves the manufacturing facility with no unique credentials, and only Trusted Users are able to provision the device with its unique credentials.

An installer uses the application and authenticates with AWS. Using the Trusted User APIs, the installer receives a temporary X.509 certificate and private key that is valid for five minutes. Using the application, the credentials are delivered to the device. The device connects to AWS IoT and exchanges the temporary credentials for a unique X.509 certificate signed with the AWS CA and a private key. During this workflow, the AWS resources including Thing name, Policy, and Certificate are set up in the AWS Account.

{{% notice note %}}
Device makers that use the Trusted User flow must develop and maintain a mobile/web application that exercises the Trusted User APIs. The Fleet Provisioning template must be set up and maintained in AWS IoT by the device maker. Optionally, an AWS Lambda function can be used to provide additional authentication steps during the provisioning process.
{{% /notice %}}
{{% notice note %}}
Devices must have the ability to accept temporary credentials over a secure connection such as Bluetooth Low Energy, WiFi, or USB. Devices must implement the logic necessary to publish and subscribe to Fleet Provisioning MQTT topics, accept the permanent credentials, and write the credentials to secure storage.
{{% /notice %}}


## Use Cases

Fleet Provisioning by Trusted User is the recommended approach when a high degree of security is needed, when the manufacturing chain is not trusted, or it is not possible to provision devices in the manufacturing chain due to technical limitations, cost, or application specific limitations. Using this approach, the credentials are never exposed to the manufacturing supply chain.

## Reference Architecture
![Trusted user](iot-cognito.svg)

The details of this flow are as follows:
1. Client authenticates against a user pool.
2. The user pool assigns 3 JWT tokens (Id, Access, and Refresh) to the client.
3. The Id JWT is passed to the identity pool and a role is chosen via the JWT claims. The user then receives IAM temporary credentials with privileges that are based on the IAM role that was mapped to the group that user belongs to.
4. The user can then make CreateProvisioningClaim call to AWS IoT Core for a specific provisioning template
5. AWS IoT Core response with temporary certificate and key pair
6. The user provisions the temporary certificate and key pair to the device, and initiate fleet provisioning with bootstrap certificate

At this point, the device have valid certificate to authenticate with AWS IoT MQTT gatwaye.


## Implementation