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

```python
# client.py - Demuestra la espera de un comando para ser evaluado y procesado
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import sys
import time


# Este ejemplo utiliza el Message Broker para AWS IoT para enviar y recibir mensajes
# a través de una conexión MQTT. Al iniciar, el dispositivo se conecta al servidor,
# se suscribe a un tema de solicitud, invoca una callback al recibir un mensaje, y
# luego responde en el tema de respuesta de vuelta a la aplicación que llama.

io.init_logging(getattr(io.LogLevel, "Info"), "stderr")

# Usando variables globales para simplificar el código de ejemplo
client_id = "device1"
endpoint = "REPLACE_WITH_YOUR_ENDPOINT_FQDN"
client_certificate = "PATH_TO_CLIENT_CERTIFICATE_FILE"
client_private_key = "PATH_TO_CLIENT_PRIVATE_KEY_FILE"
root_ca = "PATH_TO_ROOT_CA_CERTIFICATE_FILE"


# Tema para suscribirse a comandos entrantes
request_topic = "cmd/device1/req"
# Tema para enviar el resultado del comando
response_topic = "cmd/device1/resp"


# Las callbacks son el método principal para procesar eventos MQTT de manera asincrónica
# utilizando los SDKs de dispositivos.

# Callback cuando la conexión se interrumpe accidentalmente.
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")


# Callback cuando una conexión interrumpida se restablece.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(
        f"Connection resumed. return_code: {return_code} session_present: {session_present}"
    )

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # No se puede esperar sincrónicamente el resultado de la resuscripción porque estamos en el hilo del event-loop de la conexión,
        # evalúe el resultado con una callback en su lugar.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe results: {resubscribe_results}")

    for topic, qos in resubscribe_results["topics"]:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")


# Callback cuando el tema suscrito recibe un mensaje de comando
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    global response_topic
    print(f"Received command from topic '{topic}': {payload}")

    # Acción a realizar al recibir un comando, asertar True para este ejemplo
    #################################################
    ############### CÓDIGO DEL COMANDO AQUÍ ##########
    #################################################
    # result = do_something(payload)
    result = True

    if result:
        message = f"SUCCESS: command ran successfully from payload: {payload}"
    else:
        message = f"FAILURE: command did not run successfully from payload: {payload}"
    print(f"Publishing message to topic '{response_topic}': {message}")
    mqtt_connection.publish(
        topic=response_topic, payload=message, qos=mqtt.QoS.AT_LEAST_ONCE
    )


if __name__ == "__main__":
    # Crear recursos basados en el SDK
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    # Crear conexión MQTT nativa a partir de credenciales en la ruta (sistema de archivos)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=client_certificate,
        pri_key_filepath=client_private_key,
        client_bootstrap=client_bootstrap,
        ca_filepath=root_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        clean_session=False,
        keep_alive_secs=6,
    )

    print(f"Connecting to {endpoint} with client ID '{client_id}'...")

    connect_future = mqtt_connection.connect()

    # Future.result() espera hasta que un resultado esté disponible
    connect_future.result()
    print("Connected!")

    # Suscribirse
    print(f"Subscribing to topic '{request_topic}'...")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=request_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print(f"Subscribed with {str(subscribe_result['qos'])}")

    # Toda la lógica ocurre en la callback on_message_received(), bucle hasta que
    # el programa se detenga (por ejemplo, CTRL+C)
    print(f"Listening for commands on topic: {request_topic}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Desconectar
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")
```

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

```python
# application.py - Demuestra el envío de comandos a un dispositivo
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import sys
import time

# Este ejemplo utiliza el Message Broker para AWS IoT para enviar y recibir mensajes
# a través de una conexión MQTT. Al iniciar, la aplicación se conecta al servidor,
# se suscribe a un tema de respuesta que se invoca a través de una callback al recibir un mensaje.
# Los comandos se envían

io.init_logging(getattr(io.LogLevel, "Info"), "stderr")

# Usando variables globales para simplificar el código de ejemplo
client_id = "app1"
endpoint = "REPLACE_WITH_YOUR_ENDPOINT_FQDN"
client_certificate = "PATH_TO_CLIENT_CERTIFICATE_FILE"
client_private_key = "PATH_TO_CLIENT_PRIVATE_KEY_FILE"
root_ca = "PATH_TO_ROOT_CA_CERTIFICATE_FILE"

# Temas para el dispositivo de prueba objetivo
target_device = "device1"
# Tema para enviar un comando al dispositivo
request_topic = f"cmd/{target_device}/req"
# Tema para suscribirse a las respuestas de comandos
response_topic = f"cmd/{target_device}/resp"


# Las callbacks son el método principal para procesar eventos MQTT de manera asincrónica
# utilizando los SDKs de dispositivos.

# Callback cuando la conexión se interrumpe accidentalmente.
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")


# Callback cuando una conexión interrumpida se restablece.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(
        f"Connection resumed. return_code: {return_code} session_present: {session_present}"
    )

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # No se puede esperar sincrónicamente el resultado de la resuscripción porque estamos en el hilo del event-loop de la conexión,
        # evalúe el resultado con una callback en su lugar.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe results: {resubscribe_results}")

    for topic, qos in resubscribe_results["topics"]:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")


# Callback cuando el tema suscrito recibe un mensaje de comando
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    global response_topic, target_device

    print(f"Received command response on topic '{topic}' with payload: {payload}")

    # Acción a realizar al completar el comando en el dispositivo
    #################################################
    ############### CÓDIGO DEL COMANDO AQUÍ ##########
    #################################################
    # result = reconcile_command(payload)

if __name__ == "__main__":
    # Crear recursos basados en el SDK
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    # Crear conexión MQTT nativa a partir de credenciales en la ruta (sistema de archivos)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=client_certificate,
        pri_key_filepath=client_private_key,
        client_bootstrap=client_bootstrap,
        ca_filepath=root_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        clean_session=False,
        keep_alive_secs=6,
    )

    print(f"Connecting to {endpoint} with client ID '{client_id}'...")

    connect_future = mqtt_connection.connect()

    # Future.result() espera hasta que un resultado esté disponible
    connect_future.result()
    print("Connected!")

    # Suscribirse al tema de respuesta del dispositivo
    print(f"Subscribing to topic '{response_topic}'...")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=response_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print(f"Subscribed with {str(subscribe_result['qos'])}")

    # Toda la lógica ocurre en la callback on_message_received(), bucle hasta que
    # el programa se detenga (por ejemplo, CTRL+C)
    try:
        while True:
            command = input(f"Enter command to send to {target_device}: ")
            print(f"Publishing command to topic '{request_topic}': {command}")
            mqtt_connection.publish(
                topic=request_topic, payload=command, qos=mqtt.QoS.AT_LEAST_ONCE
            )
            # Wait for response text before requesting next input
            time.sleep(2)

    except KeyboardInterrupt:
        # Desconectar
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")
```

{{% /tab %}}
{{< /tabs >}}

## Consideraciones

Esta implementación cubre los aspectos básicos de un patrón de comando y control. No cubre ciertos aspectos que pueden surgir en el uso en producción.

### Mensajes duplicados o fuera de orden

En la operación normal, los mensajes de comando MQTT pueden perderse entre la _aplicación_ y el _broker_, o entre el _broker_ y el _dispositivo_. Esto puede ser causado por configuraciones de QoS, retransmisiones o reintentos de los publicadores o del _broker_, u otros errores internos de la aplicación, como un hilo bloqueado.

Para mensajes duplicados o fuera de orden, un comando debería procesarse nominalmente solo una vez, la inclusión de un id de transacción único (TID) [(ver ejemplos del patrón _Comando_)]({{< ref "/patterns/command/#examples" >}}) tanto en la solicitud como en la respuesta permite que la _aplicación_ resuelva el mensaje. Para mensajes duplicados, el _dispositivo_ puede mantener una lista de mensajes procesados recientemente y solo actuar sobre nuevos TIDs.

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
