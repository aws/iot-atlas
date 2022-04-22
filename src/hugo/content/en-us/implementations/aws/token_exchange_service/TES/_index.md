---
title: "Language Implementations"
weight: 10
summary: "AWS IoT Core Credentials endpoint enables exchanging a device certificate and key for temporary AWS credentials. The temporary credentials can then be used to make API calls against other AWS services"
---

## Use Cases

- I want to exchange an AWS IoT device certificate and key for temporary AWS credentials
- I want to use temporary AWS credentials to call other AWS services

{{% notice note %}}
For more information on authorizing direct calls to AWS services using AWS IoT Core Credential
provider, including the Token Exchange Role Alias, see [here](https://docs.aws.amazon.com/iot/latest/developerguide/authorizing-direct-aws.html).
{{% /notice %}}

## Implementation

The AWS IoT Core Credentials HTTP API is invoked with an AWS IoT device certificate and private
key. The returned temporary credentials can be used to call other AWS services via the AWS SDK by
encapsulating the HTTP API call in an AWS SDK custom credentials provider.

{{< tabs groupId="device-code">}}
{{% tab name="go" %}}

The first step in implementing the workflow is to create an HTTP client configured with TLS. The TLS
configuration uses the Amazon Root CA certificate, AWS IoT device certificate and private key. Here
we define a few helpful types and functions for creating the HTTP TLS configuration.

First we'll define a function option signature which we can use to customize our HTTP transport.

```go
// TransportOption defines the type used to implement the function option pattern used when creating
// http transports.
type TransportOption func(*http.Transport) error
```

Next we'll create a transport option which satisfies the `TransportOption` interface. We'll use this
option to add our TLS configuration to the HTTP transport. The TLS configuration uses the Amazon
Root CA certificate and the AWS IoT device certificate and private key.

```go
// WithTLS is a TransportOption which set a TLS configuration on the transport. TLS is configured
// with the provided ca certificate, device certificate, and private key. Those files must exist and
// be readable.
func WithTLS(ca, cert, key string) TransportOption {
 return func(t *http.Transport) error {
  keyPair, err := tls.LoadX509KeyPair(cert, key)
  if err != nil {
   return err
  }

  caCert, err := ioutil.ReadFile(ca)
  if err != nil {
   return err
  }

  caCertPool := x509.NewCertPool()
  caCertPool.AppendCertsFromPEM(caCert)
  t.TLSClientConfig = &tls.Config{
   RootCAs:      caCertPool,
   Certificates: []tls.Certificate{keyPair},
  }
  return nil
 }
}
```

Next we'll create a factory function which creates the HTTP transport. The HTTP transport
implementation can be customized by providing optional TransportOptions. When creating the transport
we'll supply the WithTLS option.

```go
// NewTransport returns a new HTT client transport. Transport implementations can be customized by
// providing optional TransportOptions to the factory function. Note: the factory function panics if
// an error is returned by a TransportOption.
func NewTransport(opts ...TransportOption) *http.Transport {
 transport := &http.Transport{
  ForceAttemptHTTP2:     true,
  MaxIdleConns:          10,
  ExpectContinueTimeout: 1 * time.Second,
  TLSHandshakeTimeout:   10 * time.Second,
  IdleConnTimeout:       90 * time.Second,
  Proxy:                 http.ProxyFromEnvironment,
  DialContext: (&net.Dialer{
   Timeout:   30 * time.Second,
   KeepAlive: 30 * time.Second,
  }).DialContext,
 }

 for _, opt := range opts {
  if err := opt(transport); err != nil {
   panic(err)
  }
 }

 return transport
}
```

We now have all the types and functions required to create an HTTP client for calling the AWS IoT
Core Credentials endpoint. Next we'll define the types and functions we can use to encapsulate the
API calls in an AWS SDK custom credential provider.

We'll first define the custom credential provider implementation.

```go
// provider implements the aws.CredentialsProvider interface and is the implementation for
// exchanging the AWS IoT device certificate and private key for temporary AWS credentials.
type provider struct {
 uri    string
 client *http.Client
}
```

Next we'll satisfy the AWS Credentials provider interface by implementing the `Retrieve` method. The
AWS SDK calls this method when obtaining new or refreshing expiring credentials.

```go
// Retrieve exchanges device certificate and keys for temporary AWS credentials. The process uses
// the AWS IoT credentials endpoint to obtain the AWS credentials for the AWS IAM Role mapped to an
// AWS IoT Role alias.
func (p *provider) Retrieve(ctx context.Context) (aws.Credentials, error) {
 req, _ := http.NewRequestWithContext(ctx, http.MethodGet, p.uri, nil)

 resp, err := p.client.Do(req)
 if err != nil {
  return aws.Credentials{}, fmt.Errorf("failed to exchange pki for credentials: %w", err)
 }

 defer resp.Body.Close()
 if resp.StatusCode != http.StatusOK {
  return aws.Credentials{}, fmt.Errorf("http code=%d", resp.StatusCode)
 }

 dto := struct {
  Creds struct {
   AccessKey    string `json:"accessKeyId"`
   AccessSecret string `json:"secretAccessKey"`
   SessionToken string `json:"sessionToken"`
   Expiration   string `json:"expiration"`
  } `json:"credentials"`
 }{}

 err = json.NewDecoder(resp.Body).Decode(&dto)
 if err != nil {
  return aws.Credentials{}, fmt.Errorf("failed to decode http response: %w", err)
 }

 expires, err := time.Parse(time.RFC3339, dto.Creds.Expiration)
 if err != nil {
  return aws.Credentials{}, fmt.Errorf("failed to decode expiration time format: %w", err)
 }

 return aws.Credentials{
  CanExpire:       true,
  Expires:         expires,
  AccessKeyID:     dto.Creds.AccessKey,
  SecretAccessKey: dto.Creds.AccessSecret,
  SessionToken:    dto.Creds.SessionToken,
 }, nil
}
```

Now let's create a factory function for creating the custom credential provider. The factory
function takes an HTTP client configured with TLS, the AWS IoT Token Exchange Role Alias, and AWS
IoT Core Credentials endpoint.

```go
// NewProvider returns a new CertificateProvider. The provider is used to obtain temporary AWS
// credentials from the AWS IoT Core Credentials endpoint.
func NewProvider(client *http.Client, alias, endpoint string) aws.CredentialsProvider {
 return &provider{
  client: client,
  uri:    fmt.Sprintf("https://%s/role-aliases/%s/credentials", endpoint, alias),
 }
}
```

We now have all the required components to exchange an AWS IoT device certificate and private key
for temporary AWS credentials. To use the custom credential provider when making SDK calls, we'll
create the HTTP client and AWS SDK configuration.

```go
httpClient := &http.Client{Transport: NewTransport(WithTLS(ca, cert, key))}
cfg, err := config.LoadDefaultConfig(ctx,
config.WithHTTPClient(httpClient),
config.WithCredentialsProvider(NewProvider(httpClient, alias, endpoint)))
```
