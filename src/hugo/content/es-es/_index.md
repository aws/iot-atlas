---
title: "Inicio"
---

{{< atlas-logo >}}

Bienvenido al IoT Atlas, donde los viajes exitosos utilizando el Internet de las Cosas (IoT) dependen de mapas.

Los proyectos de IoT más exitosos tienen resultados comerciales claramente definidos. La gran mayoría de los proyectos de IoT atraviesan diferentes fases, comenzando desde el prototipo, pasando por el piloto y la producción limitada hacia la producción, para lograr el resultado comercial identificado a escala. El IoT Atlas apoya su proyecto explicando el por qué, qué y quién de los diseños modernos de IoT comúnmente utilizados.

## Visión General

Muchos diseños de IoT que se están utilizando globalmente ahora son bien conocidos y probados con el tiempo, pero no son ampliamente conocidos. Los diseños a menudo provienen de dominios maduros como _redes de sensores_, arquitecturas de _[sistemas de control](https://es.wikipedia.org/wiki/Sistema_de_control)_, redes de _[máquina a máquina](https://es.wikipedia.org/wiki/M%C3%A1quina_a_m%C3%A1quina)_, y desarrollo de _[sistemas embebidos](https://es.wikipedia.org/wiki/Sistema_embebido)_. Pero la falta de visibilidad de esos diseños maduros está causando que muchas personas [reinventen la rueda](https://es.wikipedia.org/wiki/Reinventar_la_rueda) para su solución, cuando preferirían no hacerlo. Complicando aún más el asunto para los practicantes experimentados, incluso cuando se conoce un diseño de larga data, a menudo es necesario revisarlo para tener en cuenta los conceptos de desarrollo en la nube.

El IoT Atlas es un recurso tanto para nuevos como para antiguos constructores de soluciones de Internet de las Cosas. Actualiza y amplía los diseños bien conocidos con la presunción de que hoy en día, construir soluciones de "Internet de las Cosas" casi siempre significa que "una nube de hiperescala está disponible" para los practicantes que construyen cada solución. Adoptar la postura de que el desarrollo de soluciones puede depender de la existencia de una nube de hiperescala no implica que los diseños del IoT Atlas deban estar conectados para operar. En cambio, los diseños intentan aprovechar la fortaleza de una flota de dispositivos que operan localmente en entornos remotos durante largos períodos de tiempo **y** las fortalezas de la nube de escala masiva, ubicuidad global y agilidad de solución. Los diseños pueden entonces ser utilizados para construir soluciones que esperan interrupciones de red intermitentes, de larga duración o principalmente desconectadas como una influencia fundamental de sus componentes diseñados. Esencialmente, los diseños aquí siguen la filosofía de IoT de que _el borde completa la nube_.

Al partir de esta perspectiva, estamos creando un atlas que apoya la comprensión de incluso las consideraciones de IoT más complejas. Sería genial que te unas a nosotros y [contribuyas](https://github.com/aws/iot-atlas/blob/main/CONTRIBUTING.md) con tus ideas para diseños, consideraciones y ejemplos en este viaje.


## Organización

Cada diseño intenta cubrir un concepto, cubrirlo bien y, cuando tiene sentido, describir cómo el diseño actual interoperará con otros diseños. Cuando un nuevo concepto es necesario para comprender mejor un diseño, el concepto se introducirá justo a tiempo en el diseño y también se referenciará en el [glosario]({{< ref "/glossary" >}}).

Para cumplir con el estándar de publicación, un diseño completamente formado del IoT Atlas proporcionará una descripción simple de una o dos oraciones, una descripción concisa del desafío de IoT abordado, un diagrama arquitectónico y flujo de proceso no específico de un proveedor, las personas comúnmente interesadas e impactadas por las capacidades entregadas por el diseño, y consideraciones clave de implementación. Las consideraciones clave de un diseño se documentarán en el propio IoT Atlas y también a través de enlaces a recursos que proporcionen contexto adicional, como documentos técnicos, publicaciones de blogs y contenido verificado en Internet que mejor transmita lo que se debe considerar.

## Consideraciones de Diseño

#### Nivel de Abstracción

Cada diseño intenta describir el patrón a un nivel de abstracción que incorpore tantos detalles como sea posible, pero no más de los necesarios. Por supuesto, este es un equilibrio difícil de lograr y seguramente se ajustará a lo largo de la vida de este esfuerzo.

Inicialmente, el IoT Atlas describirá diseños justo **por encima** de los detalles de qué protocolo de comunicación, qué proveedor o qué lenguaje de programación podría usarse en una implementación. Por ejemplo, el diseño de [Telemetría]({{< ref "/patterns/telemetry" >}}) se describe intencionalmente justo por encima de los detalles de [CoAP](https://datatracker.ietf.org/doc/html/rfc7252), [MQTT](https://mqtt.org/) o [AMQP](https://www.amqp.org/product/architecture) y, sin embargo, alguien familiarizado con estos protocolos aún entendería el concepto del diseño sin ninguna o con solo una pequeña cantidad de transformación. Esta posición se toma porque los diseños deberían beneficiar a tantas personas como sea posible, independientemente de las herramientas y detalles específicos del proveedor. Sin embargo, los ejemplos específicos del proveedor pueden acelerar la comprensión para aquellos que están comenzando. Como tal, el IoT Atlas aceptará implementaciones de referencia de diseños, que son más específicas de lo que el pseudocódigo puede lograr.

Es poco probable que se puedan incorporar todas las perspectivas posibles, pero el objetivo de describir diseños a este nivel de abstracción está en línea con la intención principal de ayudar a los practicantes a comprender el diseño en el conjunto más amplio posible de soluciones de IoT.

#### Conceptos Clave

Los diseños en el IoT Atlas utilizarán el concepto de [temas de mensajes]({{< ref "/glossary/vocabulary#tema-de-mensaje" >}}) para transmitir el flujo detallado de mensajes entre dispositivos, entre dispositivos y componentes, o entre componentes de una solución IoT. Un tema de mensaje en este contexto debe considerarse como un mapa directo al concepto pub/sub de un [asunto](#) y como un concepto similar a las URL parciales utilizadas para describir los puntos finales de [solicitud/respuesta](#) y [REST](#). Al usar un solo concepto para describir el tema de los mensajes utilizados en el flujo de un diseño, el IoT Atlas intenta describir los conceptos de diseño de una manera más simple.

Los diseños en el IoT Atlas asumirán que un dispositivo siempre tiene un `deviceID` único para la solución. Cuando cada dispositivo tiene un ID único para la solución, cada ejemplo específico es más claro y se puede usar una lista explícita de dispositivos para implementar un diseño de una manera que soporte múltiples dispositivos. Cuando una lista de dispositivos sea crucial para el diseño, se mencionará.

#### Convenciones

Finalmente, cada diseño seguirá algunas convenciones. Para transmitir un ejemplo de datos o un concepto relacionado con el código, se utilizará la fuente `monospace` en línea; cuando una palabra o concepto sea crucial para el diseño o actúe como una definición justo a tiempo, se utilizará una tipografía en **negrita**; cuando un bloque de código sea la mejor manera de transmitir o reforzar un concepto, ese bloque se escribirá al menos como `pseudo-code` monospaced. Con el tiempo, esperamos contribuir e indexar ejemplos de cada diseño para una variedad de lenguajes y tecnologías.

## Equipo

En este momento, los mantenedores principales del IoT Atlas son [Brett Francis](https://github.com/brettf),
[Gavin Adams](https://github.com/gadams999), [Craig Williams](https://github.com/typemismatch) y [Pablo Arias](https://github.com/pabloariasmora). 


Estamos emocionados de llevar estos diseños al mundo aquí y en [GitHub](https://github.com/aws/iot-atlas); para que juntos podamos acelerar el progreso del IoT contigo.
