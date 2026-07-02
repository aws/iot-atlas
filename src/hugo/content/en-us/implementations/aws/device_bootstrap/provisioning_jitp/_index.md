---
title: "Device Bootstrap - JITP"
weight: 20
summary: "Bootstrapping device provisioning using Just-In-Time Provisioning with a registered CA certificate and provisioning template"
---

Just-In-Time Provisioning (JITP) allows IoT devices to be automatically registered and provisioned upon their first connection to AWS IoT Core. Devices are pre-loaded with a unique X.509 certificate signed by a Certificate Authority (CA) that has been registered in AWS IoT Core. When a device connects for the first time, AWS IoT Core verifies the device certificate against the registered CA and triggers a provisioning template to create the Thing, activate the certificate, and attach a policy.

{{% notice note %}}
This implementation focuses on using a self-managed CA with AWS IoT Core's JITP capability. Devices that use JITP must have certificates and private keys present on the device before onboarding. The certificates must be signed with the customer's designated CA, and that CA must be registered in AWS IoT Core. There are many device provisioning and registration options available for different types of manufacturing and distribution circumstances. Check [device bootstrap section of IoT Atlas](..) to explore other methods.
{{% /notice %}}

{{% notice note %}}
If your manufacturing chain cannot provision unique credentials at manufacturing time, consider [Fleet Provisioning by Trusted User](../fleet_provisioning_trusted_user/) or [Certificate Vending Machine](../aws-iot-certificate-vending-machine/) instead.
{{% /notice %}}

## Use Cases

JITP is a preferred method under the following conditions:

- The manufacturing chain can provision unique credentials (certificate and private key) into each device at manufacturing time.
- You have an existing PKI (self-managed or using a service like AWS Private CA) and want to leverage it for IoT device identity.
- You want zero-touch provisioning where devices register themselves on first connection without requiring a mobile app or installer.
- You need to scale device onboarding without pre-registering each device certificate individually in AWS IoT Core.
- You know which AWS account and region the device will connect to before manufacturing.

## Reference Architecture

![JITP Architecture](JITP_arch.png)

The details of this flow are as follows:
1. A private key and signed certificate pair is created using PKI. The PKI can be self-managed or use a managed service like AWS Private CA.
2. The private key and signed certificate are securely copied and stored on the device's persistent storage during manufacturing or distribution.
3. A CA certificate is registered in AWS IoT Core with a provisioning template attached. This is a one-time setup per CA.
4. The device connects to AWS IoT Core for the first time. During the TLS handshake, both the device certificate and the signing CA certificate are presented.
5. AWS IoT Core verifies the device certificate's signature against the registered CA. The provisioning template is triggered asynchronously.
6. The first TLS connection is rejected (the certificate was not yet active when the handshake started).
7. The device reconnects after a short delay. The provisioning template has created the Thing, activated the certificate, and attached the policy. The second connection succeeds.

```plantuml
@startuml
!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/InternetOfThings/all.puml
!includeurl AWSPuml/SecurityIdentityCompliance/CertificateManager.puml

skinparam participant {
    BackgroundColor AWS_BG_COLOR
    BorderColor AWS_BORDER_COLOR
}
hide footbox

participant "<$IoTGeneric>\nDevice" as device
participant "<$IoTCore>\nAWS IoT Core" as iotcore
participant "<$CertificateManager>\nProvisioning\nTemplate" as template

== One-time Setup (Manufacturer) ==
iotcore <- iotcore : Register CA certificate\n+ attach provisioning template

== Device Manufacturing ==
device <- device : Store unique certificate\n(signed by registered CA)\n+ private key

== First Connection (JITP Trigger) ==
device -> iotcore : TLS handshake\n(device cert + CA cert)
iotcore -> iotcore : Verify cert signature\nagainst registered CA
iotcore -> template : Trigger provisioning\n(async)
iotcore --> device : Connection REJECTED\n(cert not yet active)
template -> iotcore : Create Thing\nActivate certificate\nAttach policy

== Reconnection (Success) ==
device -> device : Wait 3-5 seconds\n(backoff)
device -> iotcore : TLS handshake\n(same cert + CA cert)
iotcore -> iotcore : Certificate found\nand ACTIVE
iotcore --> device : Connection ACCEPTED
device -> iotcore : SUBSCRIBE / PUBLISH

@enduml
```

{{% notice warning %}}
The first connection will always fail and disconnect. Device firmware must implement reconnection logic with exponential backoff (typically 3-5 seconds is sufficient for JITP provisioning to complete).
{{% /notice %}}

## Implementation

This section provides step-by-step implementation guidance. You need OpenSSL and the AWS CLI installed on your workstation.

### 1. Create an IAM Role for JITP

Create an IAM role that AWS IoT Core can assume during the provisioning process. Attach the `AWSIoTThingsRegistration` managed policy.

```bash
# Create the trust policy
cat > jitp-trust-policy.json << 'EOF'
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
EOF

# Create the role
aws iam create-role \
  --role-name JITPRole \
  --assume-role-policy-document file://jitp-trust-policy.json

# Attach the IoT things registration policy
aws iam attach-role-policy \
  --role-name JITPRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration
```

### 2. Create a Root CA Certificate

Generate a self-signed root CA that will sign all device certificates.

```bash
# Generate root CA private key
openssl genrsa -out deviceRootCA.key 2048

# Create OpenSSL config for CA extensions
cat > deviceRootCA_openssl.conf << 'EOF'
[ req ]
distinguished_name = req_distinguished_name
extensions = v3_ca
req_extensions = v3_ca

[ v3_ca ]
basicConstraints = CA:TRUE

[ req_distinguished_name ]
countryName = Country Name (2 letter code)
countryName_default = US
organizationName = Organization Name (eg, company)
organizationName_default = MyOrg
EOF

# Create root CA CSR
openssl req -new -sha256 -key deviceRootCA.key -nodes \
  -out deviceRootCA.csr -config deviceRootCA_openssl.conf

# Self-sign the root CA certificate (valid 10 years)
openssl x509 -req -days 3650 \
  -extfile deviceRootCA_openssl.conf -extensions v3_ca \
  -in deviceRootCA.csr -signkey deviceRootCA.key \
  -out deviceRootCA.pem
```

### 3. Register the CA with AWS IoT Core

AWS IoT Core requires proof of CA ownership via a verification certificate.

```bash
# Get the registration code for your region
aws iot get-registration-code --region <your-region>
```

Use the returned `registrationCode` as the Common Name for a verification certificate:

```bash
# Generate verification key
openssl genrsa -out verificationCert.key 2048

# Create verification CSR with registration code as CN
openssl req -new -key verificationCert.key -out verificationCert.csr \
  -subj "/CN=PASTE_REGISTRATION_CODE_HERE"

# Sign verification cert with your root CA
openssl x509 -req -in verificationCert.csr \
  -CA deviceRootCA.pem -CAkey deviceRootCA.key -CAcreateserial \
  -out verificationCert.crt -days 500 -sha256
```

### 4. Create the Provisioning Template

The provisioning template defines what AWS resources are created when a device connects via JITP. Save the following as `jitp_template.json`:

{{< code-include file="implementations/aws/device_bootstrap/provisioning_jitp/jitp_template.json" language="json" title="JITP Provisioning Template" >}}
```

{{% notice note %}}
Replace `REGION`, `ACCOUNT_ID`, and the `roleArn` value with your AWS Region, Account ID, and the ARN of the JITPRole created in Step 1. The template uses `AWS::IoT::Certificate::CommonName` as the Thing name, so ensure each device certificate has a unique Common Name.
{{% /notice %}}

### 5. Register the CA Certificate with Template

```bash
aws iot register-ca-certificate \
  --ca-certificate file://deviceRootCA.pem \
  --verification-cert file://verificationCert.crt \
  --set-as-active \
  --allow-auto-registration \
  --registration-config file://jitp_template.json \
  --region <your-region>
```

The `--allow-auto-registration` flag enables JITP. The `--registration-config` attaches the provisioning template to the CA. The response returns the CA certificate ARN.

### 6. Create a Device Certificate

For each device, generate a unique certificate signed by the registered CA:

```bash
# Generate device private key
openssl genrsa -out deviceCert.key 2048

# Create device CSR
# IMPORTANT: CommonName becomes the Thing name, Country must match the CA certificate
openssl req -new -key deviceCert.key -out deviceCert.csr \
  -subj "/CN=MyJITPDevice001/C=US/O=MyOrg"

# Sign device certificate with root CA
openssl x509 -req -in deviceCert.csr \
  -CA deviceRootCA.pem -CAkey deviceRootCA.key -CAcreateserial \
  -out deviceCert.crt -days 365 -sha256

# Combine device cert and CA cert (required for JITP - CA must be in the chain)
cat deviceCert.crt deviceRootCA.pem > deviceCertAndCACert.crt
```

### 7. Device Connection with JITP Retry Logic

Download the Amazon Root CA for server-side TLS verification:

```bash
curl -o AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
```

The following Python script demonstrates the complete device-side JITP flow, including the connect-fail-reconnect pattern using the AWS IoT Device SDK v2:

- Install SDK: `pip install awsiotsdk`
- Run: `python3 jitp_device.py --endpoint <YOUR_ENDPOINT> --cert deviceCertAndCACert.crt --key deviceCert.key --root-ca AmazonRootCA1.pem --thing-name MyJITPDevice001`

{{< code-include file="implementations/aws/device_bootstrap/provisioning_jitp/jitp_device.py" language="python" title="JITP Device - Python (AWS IoT Device SDK v2)" >}}
```

### Verification

After running the device script, verify in the AWS IoT Console:
1. Navigate to **Manage > All devices > Things** and confirm a Thing named `MyJITPDevice001` exists.
2. Navigate to **Security > Certificates** and confirm the device certificate is in `ACTIVE` state.
3. Check that the IoT policy is attached to the certificate.

```bash
# Verify via CLI
aws iot describe-thing --thing-name MyJITPDevice001 --region <your-region>
aws iot list-thing-principals --thing-name MyJITPDevice001 --region <your-region>
```

## Considerations

This implementation covers the basics of JITP. It does not cover certain aspects that may arise in production use.

### Certificate Common Name Uniqueness

Each device must have a unique Common Name in its certificate, as this becomes the Thing name via the provisioning template parameter `AWS::IoT::Certificate::CommonName`. Duplicate Common Names will cause provisioning failures. Consider using device serial numbers, MAC addresses, or UUIDs as Common Names.

### First-Connection Failure and Retry Strategy

Device firmware must handle the initial connection rejection gracefully. The JITP provisioning process is asynchronous and typically completes within 1-3 seconds. Implement exponential backoff starting at 3 seconds with a maximum of 5 retries. If all retries fail, the device should enter a diagnostic mode or report the failure through an out-of-band channel.

### CA Certificate Per Region

CA certificates are registered per AWS Region. If devices need to connect to multiple regions (for failover or geo-routing), register the same CA in each target region with the appropriate provisioning template. The device firmware can be configured with a prioritized list of endpoints.

### CA Certificate Rotation

Plan for CA certificate rotation before the CA expires. You can have multiple active CAs registered simultaneously in AWS IoT Core. The rotation strategy is:
1. Register the new CA alongside the existing one.
2. Begin signing new device certificates with the new CA.
3. Existing devices with certificates signed by the old CA continue to work.
4. After all old-CA-signed certificates have expired or been replaced, deactivate the old CA.

### Template Policy Scope

The example provisioning template uses wildcard (`/*`) resources for simplicity. In production, scope policies using template parameters:

```json
"Resource": ["arn:aws:iot:REGION:ACCOUNT_ID:client/${iot:Connection.Thing.ThingName}"]
```

This restricts each device to only connect with a client ID matching its Thing name, and publish/subscribe only to its own topics.

### Provisioning Template Hooks

For additional validation during provisioning, you can attach a [Pre Provisioning Hook](https://docs.aws.amazon.com/iot/latest/developerguide/pre-provisioning-hook.html) Lambda function to the template. This allows you to:
- Validate certificate attributes against an allowlist
- Check a device database to confirm the device is expected
- Apply conditional logic for Thing group assignment
- Reject provisioning for revoked or unexpected certificates

### Service Quotas

Be aware of AWS IoT Core [service quotas](https://docs.aws.amazon.com/iot/latest/developerguide/iot-quotas.html) related to JITP:
- Rate of `RegisterThing` transactions: consider throttling if onboarding large batches simultaneously.
- Maximum number of CA certificates per account per region.
- If onboarding thousands of devices simultaneously (e.g., factory batch activation), consider staggering connections with jitter to avoid hitting provisioning rate limits.

### Monitoring and Troubleshooting

Enable AWS IoT Core logging to CloudWatch to monitor JITP events:
- `JITP` log entries show provisioning successes and failures
- Common failure reasons: duplicate Thing name, Country field mismatch, CA not active
- Set up CloudWatch alarms on JITP failure metrics for proactive monitoring

```bash
# Enable IoT logging (one-time setup)
aws iot set-v2-logging-options \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/IoTLoggingRole \
  --default-log-level INFO \
  --region <your-region>
```

### Multi-Account Registration

If your deployment spans multiple AWS accounts (e.g., per-customer accounts), you can use [Multi-Account Registration](https://docs.aws.amazon.com/iot/latest/developerguide/x509-client-certs.html#multiple-account-cert) where the same CA is registered in multiple accounts. Each account has its own provisioning template, allowing the same device certificate format to provision into different accounts based on the endpoint the device connects to.
