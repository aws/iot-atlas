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

To experiment quickly, you can test this pattern out by using AWS Amplify and Amazon Cognito.
AWS Amplify is a set of tools and services that can be used together or on their own, to help front-end web and mobile developers build scalable full stack applications, powered by AWS.
Amazon Cognito lets you add user sign-up, sign-in, and access control to your web and mobile apps quickly and easily. Amazon Cognito scales to millions of users and supports sign-in with social identity providers, such as Apple, Facebook, Google, and Amazon, and enterprise identity providers via SAML 2.0 and OpenID Connect. 

```javascript
import logo from './logo.svg';
import './App.css';
import { withAuthenticator, AmplifySignOut } from '@aws-amplify/ui-react'
import { Auth } from 'aws-amplify';

var AWS = require('aws-sdk');
AWS.config.update({region: 'us-east-1'});

// This function is called when user clicks Create Provisioning Claim button
async function CreateProvisioningClaim() {
  try {
    // Call AWS IoT Core with the user current credentials
    // Cognito identity pool authRole should be added appropriate permissions to access AWS IoT API
    Auth.currentCredentials()
      .then(credentials => {
        const iot = new AWS.Iot({
          apiVersion: '2015-05-28',
          credentials: Auth.essentialCredentials(credentials)
        });

        // Set the name of Fleet provisioning template
        var params = {
          templateName: 'TrustedUserProvisioningTemplate'
        };
        
        // Call AWS IoT API
        iot.createProvisioningClaim(params, function(err, data) {
          if (err) console.log(err, err.stack); // an error occurred
          else     console.log(data);           // successful response
        });
      });
  } catch (error) {
    // error handling.
    alert(error);
  }
}

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <div>
          <input type="button" value="Create Provisioning Claim" onClick={CreateProvisioningClaim} />
        </div>
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <p>
          <AmplifySignOut />
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default withAuthenticator(App);
```

## Considerations

This implementation covers the basics of Amplify and React code. It does not cover certain aspects that may arise in production use.
