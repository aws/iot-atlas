---
title: "设备引导"
weight: 15
draft: true
---

{{% synopsis-bootstrap %}}
<!--more-->

## Challenge
## 挑战

IoT solutions need devices to perform some sort of privilege escalation to go from zero privilege to a fully registered and operational device in that solution. While going from *no* privilege to *full* privilege there **should** be discrete and planned steps. Each step used to gain privilege must itself follow the approach of least privilege. Additionally, there may be existing identity and privilege systems which must be incorporated into the IoT solution. 

IoT解决方案需要设备执行某种特权升级，以便在该解决方案中从零特权转变为完全注册且可操作的设备。从*零*特权到*完整*特权的转变是需要有独立且有计划的步骤。用于获得特权的每个步骤本身必须遵循最小特权的方法。此外，可能有现有的身份认证与权限系统需要包含在IoT解决方案中。

## Solution
## 解决方案

An IoT solution can manage the challenges of bootstrapping a device by deconstructing those challenges into a flow across two distinct concepts: a *registration authority* and a *privilege escalator*.  

通过将这些挑战分解为一个跨越两个不同概念的流程，IoT解决方案可以很好的应对设备引导所带来的挑战。这两个概念是：*注册机构(registration authority)*和*权限提升器(privilege escalator)*

A **registration authority** is the component that validates expected certificates, tokens, or shared credentials received from the device and then returns solution credentials for use by the device. A registration authority will at least be a collection of policies dictating the ability of un-registered devices to subscribe or publish to defined topics on the server.

**注册机构**是一个验证从设备接收的证书，令牌或共享凭证的组件。该组件返回供设备使用的解决方案凭证。注册机构至少是一组策略，规定未注册设备可以进行订阅或发布到服务器上定义主题的能力。

A **privilege escalator** enables a device with short-lived, lower-privilege credentials to share more attributes about itself or to exhibit proper behavior before obtaining higher-privileges in the solution. A distinct privilege escalation step also enables the injection of human approval into the privilege escalation process, if the solution requires. 

**权限提升器**允许具有短期低权限凭据的设备在获得解决方案中的更高权限之前，可以共享更多关于自身的属性或展示正确的行为。如果解决方案需要，权限提升流程可以增加一个单独的权限提升步骤来进行人工批准

Although there are situations where an implementation might combine registration with the ability to obtain fully escalated privileges, by breaking down the challenges as this design does, each challenge can be addressed distinctly, using new or legacy systems. 

虽然有些情况下具体实现可能会将注册与获得完全权限这两者合在一起，但如这个设计所做的将这些挑战分解，每个挑战可以使用使用新系统或遗留系统来明确解决。

The Device Bootstrap design shown in the following diagram can deliver this functionality.

下图中显示的"设备引导"设计可以提供此功能.

![Device Bootstrapping](bootstrap.png)

### Diagram Steps
1. A device registers with the registration authority using shared credentials or token.
2. The registration authority validates the authenticity of the shared credentials or token, registers the device, and returns short-lived credentials to the device.
3. A device uses the short-lived credentials to contact the privilege escalator and to share more information about itself
4. The privilege escalator determines the device's type and determines if the device should be authorized in the IoT solution. If the device is authorized, the privilege escalator returns long-lived credentials such a device certificates associated with privileges corresponding to the device's purpose within the IoT solution.
5. A device uses the long-lived privileges to subscribe and publish to the device's [messaging topic]({{< ref "/glossary/vocabulary#messaging-topic" >}})s via the server's protocol endpoint.

### 步骤说明
1. 设备使用共享凭证或令牌向注册机构注册。
2. 注册机构验证共享凭证或令牌的真实性，注册设备，并将短期凭证返回给设备。
3. 设备使用短期凭据联系权限提升器并共享有关自身的更多信息
4. 权限提升器确定设备的类型，并确定是否应在IoT解决方案中授权设备。如果设备已获得授权，则权限提升器将返回长期凭证，例如IoT解决方案中与设备用途相对应的并与权限相关联的设备证书。
5. 设备使用长期权限并通过服务器的协议端点订阅并发布到设备的[消息主题]（{{<ref“/ glossary/vocabulary＃messaging-topic”>}}）。

## Considerations
When implementing this design, consider the following questions:

## 考虑
实施此设计时，请考虑以下问题：

#### Does the device's manufacturing process create and place the initial token on the device?

#### 设备的制造过程是否会在设备上创建并放置初始令牌？

If **no**, then the device must have a mechanism to receive a secure token or [certificate](https://en.wikipedia.org/wiki/Public_key_certificate) after the device is manufactured. Such a mechanism could involve configuring a device over a Bluetooth Low Energy ([BLE](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy)) connection from a mobile application. This has the added advantage of being able to immediately associate a device to a customer while they are logged into a mobile application.

如果**不是**，则设备必须具有在设备制造后接收安全令牌或[证书](https://en.wikipedia.org/wiki/Public_key_certificate)的机制。这种机制可能涉及通过移动应用程序进行蓝牙低功耗([BLE](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy))连接来配置设备。这种机制具有额外的优点，即能够在设备登录到移动应用程序时立即将设备关联用户。

If **yes - with token/shared credentials**, In this case, it is important that the initial token or shared credentials are used to enable only the minimal privileges necessary to register with the solution. Once the registration authority validates the initial token or shared credentials, the rest of the steps of this design should be followed.

如果**是 - 使用令牌/共享凭证**，在这种情况下，非常重要的一点是使用初始令牌或共享凭证来获取注册到解决方案所需要的最小权限。一旦注册机构验证了初始令牌或共享凭证，此设计的其余步骤需要被遵循。

If **yes - with certificate**, the device can be manufactured in a secure manner and the need for a Registration Authority can be reduced if not removed altogether. This is easy to say and difficult to achieve as many manufacturing processes are purposefully disconnected from the cloud. Regardless, since the solution may have an entire step removed when keys are introduced by the manufacturer, the customer experience and overall system simplicity will benefit.

如果**是 - 使用证书**，则可以以安全的方式制造设备，注册机构也可以弱化甚至不需要了。这说起来容易做起来难，因为许多制造过程都是有意与云断开的。但无论如何，由于制造商引入密钥从而完全去掉注册机构，客户体验和整体系统的简化性都会受益。

#### How are customers associated with their devices?
#### 用户如何与他们的设备进行关联
In almost all cases when devices are provisioned, we need to associate the device to either a customer or a device profile within an established system. This involves gathering additional information from the device to complete the device registration. Gathering this additional information can be accomplished with one or a combination of the following:

在几乎所有设备配置的情况下，我们都需要将设备与用户或已有系统的设备配置文件相关联。这涉及从设备收集附加信息以完成设备注册。收集这些附加信息可以通过以下一种或多种方式完成：

* Devices are provisioned during the manufacturing process with [certificate](https://en.wikipedia.org/wiki/Public_key_certificate)s and those certificates can be pre-mapped to a device profile. This is common for solutions with large fleets of known devices.
* Devices report their model and serial numbers during their communication with the Registration Authority, that information can be pre-mapped to a device profile.
* Devices use BLE or another local form of communication to receive information about their identity, such as a customer profile. Handling this via a mobile application is the most common form of device provisioning. Using local communication can be coupled with the installation of certificates during manufacturing, enabling both the customer association and registration process to be completed in a single step.

* 通过在制造过程中使用[证书](https://en.wikipedia.org/wiki/Public_key_certificate)可以完成设备的配置，并且可以将这些证书预先映射到设备配置文件。这对于具有大量已知设备的解决方案来说是常见的。
*设备在与注册机构通信期间报告其型号和序列号，该信息可以预先映射到设备配置文件。
*设备使用BLE或其他本地通信形式来接收有关其身份的信息，例如客户资料。通过移动应用程序处理这是最常见的设备配置形式。使用本地通信可以在制造期间与证书的安装相结合，使得客户关联和注册过程能够在单个步骤中完成。

#### Are you using device certificates?
Although the thought of trying to provision every single device in a solution with a certificate can be daunting, it is by far the most secure way to provision devices. It is important to establish mutual authentication to prevent threats like [man-in-the-middle](https://en.wikipedia.org/wiki/Man-in-the-middle_attack) attacks. When bootstrapping your devices, certificates should always be your first choice for device identity.

#### Does the registration authority need to support custom authorization integration with an existing customer solution?
If **yes**, the design's registration authority step can be implemented using an Application Programming Interface ([API](https://en.wikipedia.org/wiki/Application_programming_interface)) in front of an existing customer solution. This API can then perform the registration authority job while leveraging the customer's existing solution.

## Examples

    <tbd written scenario>