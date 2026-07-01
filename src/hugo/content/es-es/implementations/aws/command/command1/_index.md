---
title: "Comando - Temas MQTT"
weight: 10
summary: "Comando y control de un dispositivo usando temas MQTT"
---

El comando y control es la operación de enviar un mensaje a un dispositivo solicitando que realice alguna acción. Opcionalmente, el dispositivo puede reconocer que ha logrado o fallado en completar la acción.

{{% notice note %}}
Esta implementación se centra en el uso de temas MQTT para realizar patrones de solicitud y respuesta (por ejemplo, comando y control). Consulte el [Diseño de Temas MQTT para AWS IoT Core](https://docs.aws.amazon.com/whitepapers/latest/designing-mqtt-topics-aws-iot-core/designing-mqtt-topics-aws-iot-core.html), específicamente la sección _Uso de Temas MQTT para Comandos_. Este documento técnico proporciona patrones de temas alternativos que van más allá del alcance de esta implementación.
{{% /notice %}}

## Casos de Uso

- Acción casi en tiempo real cuando se emite un comando a un dispositivo
  - _Quiero que la luz se encienda cuando presione un botón desde mi aplicación móvil_
- Interactuar con un periférico, actuador u operación de un dispositivo
  - _Quiero encender o apagar el LED en mi dispositivo_
  - _Quiero reiniciar el dispositivo de forma remota_
- Solicitar datos o estado del dispositivo
  - _Quiero que el dispositivo publique el último archivo de registro en un tema_
- Actualizar la configuración operativa o de guardado del dispositivo
  - _Quiero aumentar la frecuencia actual de telemetría emitida en mi dispositivo_
  - _Quiero cambiar la configuración guardada de mis dispositivos que entrará en vigor en el próximo reinicio_

## Arquitectura de Referencia

![Comando y control a través de temas MQTT](architecture.svg)

- _AWS IoT Core_ es el broker de mensajes MQTT que procesa mensajes en nombre de los clientes
- _Dispositivo_ es el objeto IoT que se va a controlar
- _Aplicación_ es la lógica remota que emite comandos

1. El _Dispositivo_ establece una conexión MQTT con el endpoint de _AWS IoT Core_, y luego se suscribe al tema `cmd/device1/req` (solicitud). Este es el tema donde se recibirán y procesarán los mensajes entrantes.
1. La _Aplicación_ establece una conexión MQTT con el endpoint de _AWS IoT Core_, y luego se suscribe al tema `cmd/device1/resp` (respuesta). Este es el tema donde se recibirán los mensajes de reconocimiento del dispositivo.
1. Para enviar un comando, la _Aplicación_ publica un mensaje en el tema `cmd/device1/req`, y el dispositivo recibe el mensaje en su suscripción a ese tema y realiza alguna acción.
1. (Opcional) Una vez que el comando ha sido procesado, el dispositivo publica el resultado de la acción en el tema `cmd/device1/resp`. La _Aplicación_ recibe el mensaje de respuesta y reconcilia la acción pendiente.

{{% center %}}

```plantuml
@startuml
!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/InternetOfThings/all.puml
!includeurl AWSPuml/General/Client.puml

'Comentar para usar el formato de secuencia predeterminado de PlantUML
skinparam participant {
    BackgroundColor AWS_BG_COLOR
    BorderColor AWS_BORDER_COLOR
}
'Hide the bottom boxes
hide footbox

participant "<$IoTGeneric>\nDevice" as device
participant "<$IoTCore>\nMQTT Broker" as broker
participant "<$Client>\nApplication" as app

== Connect and subscribe ==
device -> broker : connect(iot_endpoint)
device -> broker : subscribe("cmd/device1/req")
app -> broker : connect(iot_endpoint)
app -> broker : subscribe("cmd/device1/resp")

== Command operation and (optional) response ==
app -> broker : publish("cmd/device1/req", "light: on", "id: 1111")
broker -> device : publish("cmd/device1/req", "light: on", "id: 1111")
device -> device : Turn on light
device -> broker : publish("cmd/device1/resp", "success", id: "1111")
broker -> app : publish("cmd/device1/resp", "success", id: "1111")
app -> app : reconcile("id: 1111")
@enduml
```

{{% /center %}}

### Suposiciones

Este enfoque de implementación asume que el _Dispositivo_ está conectado en todo momento, suscrito a un tema para recibir comandos entrantes, y puede recibir y procesar el comando. También asume que el _Dispositivo_ puede notificar a la _Aplicación_ que envía que el comando fue recibido y procesado si es necesario. Finalmente, se asume que los tres participantes reciben, reenvían y actúan sobre los flujos de mensajes en ambas direcciones con éxito.

## Implementación

Tanto la _Aplicación_ como el _Dispositivo_ utilizan enfoques similares para conectarse, enviar y recibir mensajes. Los ejemplos de código a continuación son completos para cada participante.

{{% notice note %}}
Los ejemplos de código se centran en el diseño del _comando_ en general. Consulte la [Guía de inicio de AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html) para obtener detalles sobre la creación de cosas, certificados y la obtención de su endpoint. Los ejemplos de código a continuación se utilizan para demostrar la capacidad básica del patrón de _Comando_.
{{% /notice %}}

### Dispositivo

El código del _Dispositivo_ se centra en conectarse al _Broker_ y luego suscribirse a un tema para recibir comandos. Al recibir un comando, el _Dispositivo_ realiza alguna acción local y luego publica el resultado (éxito, fallo) del comando de vuelta a la _Aplicación_, que luego puede reconciliar el comando.

El _Dispositivo_ continuará recibiendo y respondiendo a comandos hasta que se detenga.

{{< tabs groupId="device-code">}}
{{% tab name="python" %}}
Consulte este [ejemplo de pubsub](https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/pubsub.py) para más detalles.

- Instale el SDK desde PyPI: `python3 -m pip install awsiotsdk`
- Reemplace las variables globales con un endpoint, clientId y credenciales válidos
- Inicie en una sesión de terminal separada antes de ejecutar la _Aplicación_: `python3 client.py`

{{< code-include file="implementations/aws/command/command1/client.py" language="python" title="client.py - Código del Dispositivo" >}}

{{% /tab %}}
{{< /tabs >}}


### Aplicación

El código de la _Aplicación_ se conecta al Broker y se suscribe al tema de respuesta del _Dispositivo_. Luego espera a que se ingrese un comando y lo envía al tema de solicitud del _Dispositivo_.

{{< tabs groupId="device-code">}}
{{% tab name="python" %}}

Consulte este [ejemplo de pubsub](https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/pubsub.py) para más detalles.

- Instale el SDK desde PyPI: `python3 -m pip install awsiotsdk`
- Reemplace las variables globales con un endpoint, clientId y credenciales válidos
- Inicie en una sesión de terminal separada después de que el código del _Dispositivo_ esté en ejecución: `python3 application.py`

{{< code-include file="implementations/aws/command/command1/application.py" language="python" title="application.py - Código de la Aplicación" >}}

{{% /tab %}}
{{< /tabs >}}

## Consideraciones

Esta implementación cubre los aspectos básicos de un patrón de comando y control. No cubre ciertos aspectos que pueden surgir en el uso en producción.

### Mensajes duplicados o fuera de orden

En la operación normal, los mensajes de comando MQTT pueden perderse entre la _aplicación_ y el _broker_, o entre el _broker_ y el _dispositivo_. Esto puede ser causado por configuraciones de QoS, retransmisiones o reintentos de los publicadores o del _broker_, u otros errores internos de la aplicación, como un hilo bloqueado.

Para mensajes duplicados o fuera de orden, un comando debería procesarse nominalmente solo una vez, la inclusión de un id de transacción único (TID) [(ver ejemplos del patrón _Comando_)]({{< ref "/patterns/command/#ejemplos" >}}) tanto en la solicitud como en la respuesta permite que la _aplicación_ resuelva el mensaje. Para mensajes duplicados, el _dispositivo_ puede mantener una lista de mensajes procesados recientemente y solo actuar sobre nuevos TIDs.

Para mensajes fuera de orden, el TID puede abarcar un número o secuencia incremental, y el _dispositivo_ puede rastrear el orden de los mensajes recibidos. Otro enfoque podría ser usar una [marca de tiempo](https://en.wikipedia.org/wiki/Timestamp) para un TID donde el _dispositivo_ rastrea el último mensaje procesado y si recibe uno con una marca de tiempo anterior, puede descartar o actuar sobre este mensaje fuera de orden.

Cuando se trata de mensajes de _comando_ que necesitan ser procesados en un cierto orden (por ejemplo, **A**, luego **B**, luego **C**), tanto el _dispositivo_ como la _aplicación_ deben acordar un estado de comandos y responder en consecuencia si llegan fuera de orden. Por ejemplo, si un _dispositivo_ recibe el comando **A** (válido) y luego el comando **C** (inválido ya que el siguiente comando debería haber sido **B**), debería informar un fallo y notificar a la _aplicación_ que llama sobre su estado actual.

### Mensajes perdidos o dispositivo desconectado durante la entrega

Otra consideración es cómo se debe rastrear y procesar un mensaje de comando si nunca se entrega. Es común que los dispositivos IoT estén desconectados del _broker_ durante períodos de tiempo. Esto podría deberse a que el dispositivo está apagado, a cortes locales o generalizados del ISP, o a problemas intermitentes de la red. Además, incluso con el uso de un [QoS de 1](https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html#mqtt-qos), todavía existe la posibilidad de pérdida de mensajes.

La _aplicación_ debe tener lógica para rastrear comandos pendientes, como un temporizador para retransmitir el comando si no recibe una respuesta en un cierto período de tiempo con [lógica de reintento](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/). En caso de que el dispositivo no responda dentro de un período de tiempo establecido, la _aplicación_ puede generar un error de conectividad del dispositivo.

Desde la perspectiva del _dispositivo_, si está desconectado durante el procesamiento de un comando o una serie de comandos, el _dispositivo_ debe publicar un error una vez que se vuelva a conectar. Esto puede dar a la _aplicación_ que realiza la solicitud el contexto sobre cómo proceder.

### Difusión a un Grupo de Dispositivos Relacionados

Esta implementación se centra en la interacción de una sola _aplicación_ y _dispositivo_. Algunos casos de uso pueden tener un solo comando que afecta a múltiples dispositivos. Por ejemplo, una _aplicación_ puede solicitar que todas las luces de advertencia de un piso de fábrica se enciendan en caso de emergencia. O, podría estar solicitando a una flota de dispositivos que informen su configuración y estado actual.

Para un pequeño grupo de _dispositivos_, un enfoque podría ser que la _aplicación_ envíe un comando individual a cada dispositivo y reconcilie la respuesta.

Sin embargo, cuando el grupo de _dispositivos_ objetivo es grande, esto requeriría que la _aplicación_ envíe 1 por _dispositivo_. En este caso, los _dispositivos_ podrían suscribirse a un tema común para tipos de mensajes de difusión, y la aplicación solo necesita enviar un solo mensaje y reconciliar las respuestas individuales de los _dispositivos_.

Por ejemplo, `device1`, `device2` y `device3` pueden suscribirse al tema `device_status/request`. Cuando la _aplicación_ publica un mensaje en ese tema, cada dispositivo recibirá una copia del mensaje, podrá actuar en consecuencia y luego cada uno podrá publicar su respuesta en un tema común `device_status/response`, mencionando su ID de dispositivo en el payload. La _aplicación_ o el [Motor de Reglas de AWS IoT](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rules.html) pueden reconciliar las respuestas. Este patrón se cubre en el [documento técnico sobre el diseño de temas MQTT para AWS IoT Core](https://docs.aws.amazon.com/whitepapers/latest/designing-mqtt-topics-aws-iot-core/mqtt-design-best-practices.html).
