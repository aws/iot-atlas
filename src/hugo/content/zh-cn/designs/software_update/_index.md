---
title: "软件更新"
weight: 70
---

<!-- {{< synopsis-software-update >}} -->

要求设备获取新软件，对自身进行更新并确认完成。

<!--more-->

## 挑战

IoT 解决方案需要为设备提供更新自己软件的机制。无需人工干预的软件更新的支持，对于将解决方案扩展到数百万台设备以及提供出色的客户体验都是至关重要。然而，以安全、可扩展和可靠的方式实现大量设备的全量更新需要可扩展以满足设备负载的解决方案、弹性的命令机制以及可以跟踪整个设备组状态的方法。

## 解决方案

利用["命令"]({{<ref "/designs/command">}})和["设备状态副本"]({{<ref "/designs/device_state_replica">}})设计的 IoT 解决方案，加上一个全球可用且可扩展的存储解决方案，足以应对大量设备进行软件更新时所带来的所有挑战。

如下图所示的软件更新的模式可以提供这样的功能。

![Software Update](software-update.png)

### 步骤说明

1. 设备订阅差异[消息主题]({{< ref "/glossary/vocabulary#消息主题message-topic" >}}) `state/deviceID/update/delta` 并从设备状态副本接收到设备相关的状态变化消息。
2. 应用程序获取新的软件更新包并将其放置在一个可被生产设备访问到的存储解决方案中。
3. 应用程序确认需要接收新软件包的设备，并向设备的主题`state/deviceID/update`发布一条期望状态消息。该消息包含一个软件更新的 URL，该 URL 与设备当前软件版本的 URL 是不同的
4. 追踪该设备的设备状态副本会将期望设备状态记录在一个持久化数据存储中，并向主题`state/deviceID/update/delta`发布一条差异消息，该消息会被发送到设备。
5. 设备获取到差异消息，该消息做为“软件更新”的命令控制消息。具体而言，该消息传递了当前软件版本 URL 和新 URL 之间的变化
6. 设备从差异消息获取到新的软件更新 URL
7. 设备下载新版本软件并在本地进行软件更新
8. 设备向更新主题`state/deviceID/update`发布一条确认消息，反馈设备当前所使用的软件版本。追踪该设备的软件状态副本会将新状态记录在一个持久化数据存储中。
9. 设备状态副本向主题`state/deviceID/update/accepted`发布一条消息，确认软件更新已经完成。

## 考虑点

当实现这个设计时，请考虑如下问题：

#### 目标设备如何从给定 URL 获取软件升级包, 并确保只有该设备能够获取？

通过使用**预签名 URL**或者**临时凭证**，解决方案可以确保只有需要进行软件更新的目标设备才能获取软件更新包。这两种方法有不同的考虑点。

**预签名 URL**　- 预签名 URL 的好处是它能够限制设备只能在一段时间内进行软件更新，或是设备需要有特定公共 IP 地址才能下载软件更新。当下载软件更新包的设备没有可公开解析的 IP 地址时，这种方法的不利之处就会显现出来。如果没有公开可解析的 IP 地址，解决方案只能在软件更新上设置时间限制。解决方案的实践者可能会或者可能不会认为这是可接受的。

**临时凭证** - 设备与解决方案进行交互，以获取一个仅有存储访问权限的临时凭证以便下载软件更新。使用临时凭证的好处是只有拥有该凭证的设备才能访问软件更新，即使该设备没有可公开解析的 IP 地址也是如此。这种方法稍微不好的地方在于设备和解决方案会变得更加复杂，因为设备需要经过一个单独的流程来获取临时凭证。

## 示例

### 从设备端视角看软件更新

设备在 IoT 解决方案中通过[设备状态副本]({{<ref "/designs/device_state_replica">}})获取并执行“更新”命令的逻辑示例如下。具体而言，设备将获得新软件，使用该软件执行更新，并确认完成。

#### 设备对更新命令消息进行准备

设备通过订阅一个消息监听函数，处理来自`state/deviceID/update/delta`主题的[命令消息]({{<ref "/glossary/vocabulary#命令消息command-message">}})

```python
def message_listener(message):
    # ..do something with 'message'..

def main():
    # subscribe the message listener function to the topic
    sub = topic_subscribe('state/deviceID/update/delta', message_listener)
    # now wait until the program should end
    wait_until_exit()
```

#### 设备从消息中读取下载 URL 并下载软件更新

过了一段时间后，设备收到一个差异消息，该消息是'软件更新'命令消息

```python
def message_listener(message):
    # parse the message from raw format into something the program can use
    msg = parse_message(message)
    # determine if the message is an update command type
    if msg is UPDATE_COMMAND:
        # get the globally unique job ID from the command message
        job_id = msg.get_job_id()
        # read the software update URL from the command message
        url = msg.read_value('softwareURL')
        # download the software from the given URL
        software = download_software(url)
        # ..and apply the software update triggered by the specific job ID
        apply_software(software, job_id)
```

#### 设备应用软件更新并发布确认消息

设备执行更新并将执行更新的结果发布到`state/deviceID/update/accepted`主题上以完成对命令的确认

```python
def apply_software(software, job_id):
    # do the local, device-specific work to apply the software
    # and produce a result value of SUCCESS or FAILURE

    if result is SUCCESS:
        # make a success message
        message = 'jobID:' + job_id + " SUCCESS"
    else:
        #make a failure message
        message = 'jobID:' + job_id + "FAILURE"

    # the topic used to publish the acknowledge message
    topic = 'state/deviceID/update/accepted'
    # ...and finally, publish the acknowledge message
    message_publish(topic, message, quality_of_service)
```
