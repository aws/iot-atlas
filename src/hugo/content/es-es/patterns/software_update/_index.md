---
title: "Actualización de Software"
weight: 70
aliases:
  - /designs/software_update/
summary: "Pedir a un dispositivo que obtenga nuevo software, realice una actualización en sí mismo y confirme la finalización."
---

## Desafío

Las soluciones IoT deben proporcionar un mecanismo para que los dispositivos actualicen su propio software. Soportar actualizaciones de software sin intervención humana es fundamental tanto para escalar soluciones a millones de dispositivos como para ofrecer una excelente experiencia al cliente. Sin embargo, lograr una actualización completa de grandes conjuntos de dispositivos de manera segura, escalable y confiable requiere una solución que pueda escalar para manejar la carga de dispositivos, un mecanismo de comando resiliente y una forma de rastrear el estado de toda la flota de dispositivos.

## Solución

Las soluciones IoT que aprovechan los patrones de diseño de [Comando]({{< ref "/patterns/command" >}}) y [Réplica del Estado del Dispositivo]({{< ref "/patterns/device_state_replica" >}}) junto con una solución de almacenamiento globalmente disponible y escalable son capaces de enfrentar todos los desafíos inherentes a la actualización del software de dispositivos en una gran flota.

El patrón de Actualización de Software mostrado en el siguiente diagrama puede proporcionar esta funcionalidad.

![Actualización de Software](software-update.png)

### Pasos del Diagrama

### Pasos del Diagrama

1. Un dispositivo se suscribe al [tema de mensajes]({{< ref "/glossary/vocabulary#message-topic" >}}) delta `state/deviceID/update/delta` sobre el cual llegarán los mensajes de cambio de estado relacionados con el dispositivo desde la réplica del estado del dispositivo.
2. Una aplicación obtiene la nueva distribución de software y la coloca en una solución de almacenamiento accesible para los dispositivos de producción.
3. Una aplicación identifica un dispositivo que debe recibir el nuevo software y publica un mensaje de estado deseado en el tema `state/deviceID/update` del dispositivo. El mensaje de estado deseado contiene una URL de actualización de software diferente a la URL de la versión actual del software del dispositivo.
4. La réplica del estado del dispositivo que rastrea este dispositivo registra el estado deseado del dispositivo en un almacén de datos persistente y publica un mensaje delta en el tema `state/deviceID/update/delta` que se envía al dispositivo.
5. El dispositivo recibe un mensaje delta que actúa como el mensaje de comando de 'actualización de software'. Específicamente, este mensaje transmite el cambio entre la URL de la versión actual del software y la nueva URL.
6. El dispositivo obtiene la nueva URL de actualización de software del mensaje delta.
7. El dispositivo descarga el nuevo software y aplica el software localmente.
8. El dispositivo publica un mensaje de reconocimiento reflejando la versión del software que el dispositivo está utilizando ahora en el tema de actualización `state/deviceID/update` y una réplica del estado del dispositivo que rastrea este dispositivo registra el nuevo estado en un almacén de datos persistente.
9. La réplica del estado del dispositivo publica un mensaje en el tema `state/deviceID/update/accepted`. La actualización de software ahora se considera completa.

## Consideraciones

Al implementar este patrón, considere las siguientes preguntas:

#### ¿Cómo obtiene el dispositivo de destino y solo ese dispositivo la actualización de software de la URL proporcionada?

La solución puede asegurar que solo el dispositivo destinado a una actualización de software pueda obtener la actualización utilizando una **URL pre-firmada** o una **credencial temporal**. Cada enfoque tiene diferentes consideraciones.

**URL pre-firmada** - el beneficio de una URL pre-firmada es que limita la capacidad de un dispositivo para descargar una actualización de software dentro de un período de tiempo y por dispositivos con direcciones IP públicas específicas. El aspecto negativo de este enfoque surge cuando el dispositivo que descarga la actualización no tiene una dirección IP resoluble públicamente. Sin una dirección IP resoluble públicamente, la solución solo puede establecer un límite de tiempo en la interacción con la actualización de software. El practicante de una solución puede o no encontrar esto aceptable.

**Credencial temporal** - un dispositivo interactúa con la solución para obtener una credencial temporal asociada solo con el privilegio de acceder a la solución de almacenamiento para descargar la actualización. El beneficio de usar una credencial temporal es que solo el dispositivo con esa credencial puede acceder a la actualización, incluso cuando el dispositivo no tiene una dirección IP resoluble públicamente. El pequeño aspecto negativo de este enfoque es que requiere que el dispositivo y la solución sean más complejos porque el dispositivo debe pasar por un proceso separado para obtener credenciales temporales.

## Ejemplo

### Perspectiva del dispositivo en una actualización de software

Un ejemplo de la lógica involucrada para que un dispositivo en una solución IoT reciba y ejecute un comando de "actualización" recibido a través de una [Réplica del Estado del Dispositivo]({{< ref "/patterns/device_state_replica" >}}). Específicamente, el dispositivo obtendrá nuevo software, realizará una actualización utilizando ese software y reconocerá la finalización.

#### El dispositivo se prepara para los mensajes de comando de actualización

Un dispositivo suscribe una función de escucha de mensajes para procesar [mensajes de comando]({{< ref "/glossary/vocabulary#command-message" >}}) provenientes del tema `state/deviceID/update/delta`

```python
def message_listener(message):
    # ..do something with 'message'..

def main():
    # subscribe the message listener function to the topic
    sub = topic_subscribe('state/' + device_id + '/update/delta', message_listener)
    # now wait until the program should end
    wait_until_exit()
```

#### El dispositivo lee la URL de descarga del mensaje y descarga el software

Después de un tiempo, el dispositivo recibe un mensaje delta que actúa como el mensaje de comando de 'actualización de software'.

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

#### El dispositivo aplica el software y publica un mensaje de reconocimiento

Un dispositivo aplicará el software descargado y reconocerá la finalización del comando con un mensaje al tema `state/deviceID/update`.

```python
def apply_software(software, job_id):
    # do the local, device-specific work to apply the software
    # and produce a result value of SUCCESS or FAILURE

    if result is SUCCESS:
        # make a success message
        message = 'jobID:' + job_id + " SUCCESS"
    else:
        #make a failure message
        message = 'jobID:' + job_id + " FAILURE"

    # the topic used to publish the acknowledge message
    topic = 'state/deviceID/update'
    # ...and finally, publish the acknowledge message
    message_publish(topic, message, quality_of_service)
```
