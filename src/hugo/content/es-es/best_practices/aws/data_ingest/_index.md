---
title: "Mejores Prácticas de Ingesta de Datos de AWS IoT"
weight: 50
summary: "Mejores prácticas para la ingesta de datos con AWS IoT"
---

## Bienvenido

Una característica clave de cualquier aplicación IoT es la recopilación de datos de una flota de dispositivos, y poder procesar y analizar esos datos en la nube. **Ingesta** - donde los datos se reciben de los dispositivos y se envían para su procesamiento - es una etapa crítica en este flujo de trabajo. Al diseñar su aplicación con AWS IoT, hay varios factores y métodos a considerar con respecto a la ingesta de los datos de sus dispositivos, y pueden presentar diferentes compensaciones.

Siguiendo algunas mejores prácticas, puede asegurarse de que la capa de ingesta de su aplicación esté más alineada con sus necesidades comerciales específicas y con los pilares del [**AWS Well-Architected Framework**](https://aws.amazon.com/architecture/well-architected): Optimización de Costos, Eficiencia de Rendimiento, Confiabilidad, Seguridad y Excelencia Operacional.

In the sections below, best practices are organized by pillar.  However, please note that some best practices have impact across multiple.  For optimal results, you should evaluate your IoT application from the perspective of all five pillars.

En las secciones a continuación, las mejores prácticas están organizadas por pilar. Sin embargo, tenga en cuenta que algunas mejores prácticas tienen impacto en múltiples pilares. Para obtener resultados óptimos, debe evaluar su aplicación IoT desde la perspectiva de los cinco pilares.

* [Optimización de Costos](#cost)  
* [Eficiencia de Rendimiento](#eficioencia-de-rendimiento)   
* [Confiabilidad](#confiabilidad) 
* [Seguridad](#seguridad)  
* [Excelencia Operacional](#excelencia-operacional)

Consideraciones y recomendaciones adicionales relacionadas con la ingesta se pueden encontrar en la [sección de Apéndice](#apendice).

<a name="cost"></a>

-----
## Consideraciones de Optimización de Costos:

#### Aproveche el procesamiento local para agregar, agrupar, filtrar o comprimir las cargas útiles de los mensajes en el Edge para una mayor eficiencia

**El procesamiento local o en el Edge** se refiere al trabajo que podemos hacer en nuestros dispositivos de hardware IoT para facilitar una ingesta de datos más eficiente a la nube. Hay diferentes formas de aprovechar esto, y depende de sus necesidades, y de las capacidades y limitaciones de su hardware y red.

Algunas preguntas clave a considerar:

* ¿Con qué frecuencia requiere su aplicación que se envíen mensajes (datos) desde los dispositivos? ¿Requiere un flujo constante de mensajes pequeños (para telemetría frecuente o actualizaciones)? ¿O puede agrupar mensajes durante un cierto intervalo (por ejemplo, minutos)?

* Esto informará la frecuencia de los mensajes de su dispositivo hacia la nube. Donde los mensajes periódicos hacia la nube sean adecuados, su dispositivo puede combinar múltiples mensajes pequeños en lotes para una mayor eficiencia de transmisión. Vea [Acerca del Tamaño de los Mensajes](#messagesize) a continuación.

* ¿Hay valor comercial en transmitir todos los datos de sus dispositivos a la nube? ¿O puede resumir datos, eliminar valores duplicados, truncar o ignorar ciertas categorías para transmitir menos datos en general?  

* Esto informará si puede tomar medidas para reducir la cantidad de mensajes y el tamaño correspondiente de la carga útil, lo que puede ahorrar en mensajería y en costos de almacenamiento y procesamiento posteriores. El procesamiento local puede aprovecharse para realizar estas operaciones. Por ejemplo, considere si puede ignorar ciertos eventos de manera segura. En tales casos, su dispositivo puede filtrar esos eventos para evitar incurrir en los costos de transmitirlos y procesarlos.

* Si puede reducir el número de decimales/precisión de los valores, o abreviar ciertos valores de texto para hacerlos más cortos, puede lograr un tamaño de mensaje/conteo de bytes más pequeño.

* En situaciones donde se debe enviar datos de telemetría, _¿necesita incluir todos los datos sin procesar?_ Por ejemplo, puede aprovechar el procesamiento local para agregar o promediar los valores de los datos, y solo enviar los resultados resumidos a la nube.

También puede usar marcos de serialización para comprimir la carga útil del mensaje. <b>Advertencia</b>: esto es más adecuado para casos de uso donde las Reglas de IoT no necesitan inspeccionar directamente la carga útil del mensaje, ya que será ilegible en su estado codificado.

<a name="messagesize"></a>
##### Acerca del Tamaño de los Mensajes:

Los mensajes de AWS IoT Core se miden en incrementos de 5KB, con un tamaño máximo de mensaje de 128KB.
Por ejemplo, un mensaje de 2KB tiene el mismo costo que un mensaje de 5KB, y un mensaje de 6KB tiene el mismo costo que un mensaje de 10KB.

Asumiendo que sus dispositivos no están limitados por hardware, para una eficiencia óptima, intente mantener el tamaño del mensaje lo más cercano posible a los 5KB, y considere agrupar varios mensajes más pequeños (<5KB) en uno más grande.

**Advertencia:** Equilibre el tamaño del batch contra el retraso de transmisión y el riesgo de perder un mensaje que contenga múltiples eventos agrupados, para su aplicación.

<br>

{{% notice nota %}}
Ciertas optimizaciones pueden agregar complejidad y retrasos al procesamiento de mensajes, lo cual debe evaluarse cuidadosamente frente a cualquier beneficio de ahorro de costos.
{{% /notice %}}


##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-20-4.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-21-2.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/optimizing-over-time.html  

<br>

#### Use IoT Core’s Basic Ingest para ahorrar en costos de mensajería

[Precios de AWS IoT Core](https://aws.amazon.com/iot-core/pricing) se basan en algunos componentes diferentes.

**Basic Ingest** le permite enviar datos entrantes del dispositivo directamente a otros servicios de AWS a través de acciones de reglas de IoT, sin incurrir en los costos de mensajería de IoT Core. Otros componentes de costos de IoT Core seguirán aplicándose.

Basic Ingest ayuda a optimizar la ingesta de datos de alto volumen al omitir el broker de mensajes de publicación/suscripción dentro de AWS IoT Core, y enviar los datos directamente a reglas de IoT predefinidas asociadas con temas reservados de Basic Ingest (use un prefijo $).

**Advertencia:** Otros dispositivos y reglas no pueden suscribirse a estos temas. Si se requieren múltiples suscriptores, use un tema estándar en su lugar.

us dispositivos pueden usar una combinación de temas estándar y de Basic Ingest, según sea necesario, para lograr la mejor combinación para la optimización de costos.

Por ejemplo, si su caso de uso implica datos entrantes del dispositivo que van directamente a [servicios específicos de AWS](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rule-actions.html) como DynamoDB, Kinesis, S3, IoT Analytics o Lambda, puede aprovechar Basic Ingest para lograr mayores ahorros de costos.

##### Más información: 
https://docs.aws.amazon.com/iot/latest/developerguide/iot-basic-ingest.html  
https://docs.aws.amazon.com/iot/latest/developerguide/iot-rule-actions.html  
https://docs.aws.amazon.com/whitepapers/latest/designing-mqtt-topics-aws-iot-core/mqtt-design-best-practices.html

<br>

#### O, envíe datos de telemetría de alto volumen directamente a un servicio de almacenamiento intermedio

En escenarios de telemetría y video de alto volumen, puede ser más rentable omitir AWS IoT Core para la ingesta y enviar los datos entrantes del dispositivo directamente a un buffer/stream como Amazon Kinesis Data Streams o Amazon Kinesis Video Streams, mientras se mantiene por separado el comando y control de la flota a través de AWS IoT Core.

**Advertencia:** No puede usar el motor de reglas de AWS IoT Core en los datos ingeridos de esta manera, y necesitaría implementar su propia lógica utilizando otros medios, como con funciones de AWS Lambda.

<a name="cost_datalake"></a>

#### Use un data lake para los datos ingeridos

Un [**data lake**](https://aws.amazon.com/big-data/datalakes-and-analytics/what-is-a-data-lake) es un repositorio centralizado que le permite almacenar todos sus datos estructurados y no estructurados a cualquier escala. Típicamente construido alrededor de Amazon S3, el data lake es flexible, puede extenderse con otros almacenes especializados para acomodar grandes cantidades y variedades de datos, y sirve como fuente para análisis.

Para cada caso de uso de telemetría IoT, seleccione un formato de datos y un almacén de datos que coincidan de manera rentable con las características de los datos, los patrones de uso previstos y los requisitos del ciclo de vida.

Dependiendo de su caso de uso, los datos de IoT pueden ser ingeridos a través de AWS IoT Core y enviados a Amazon S3 usando reglas de IoT, o aterrizados por otros medios, como Amazon Kinesis Data Firehose, o haciendo que los dispositivos IoT escriban datos en lotes directamente en Amazon S3.

A medida que los datos envejecen, gestione su ciclo de vida de acuerdo con las políticas de retención de datos de su organización. Por ejemplo, herramientas como [políticas de ciclo de vida de S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html) o [S3 Intelligent Tiering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering-overview.html) pueden ayudar a automatizar el movimiento de datos a niveles de acceso infrecuente y archivo más rentables.

En lugar de construir su propia solución, también puede aprovechar servicios gestionados como [AWS IoT Analytics](https://aws.amazon.com/iot-analytics). Este servicio recopila, preprocesa, enriquece, almacena y analiza los datos de los dispositivos IoT que usted le envía.

##### Más información:
https://aws.amazon.com/big-data/datalakes-and-analytics/what-is-a-data-lake  
https://aws.amazon.com/big-data/datalakes-and-analytics/data-lake-house/
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-20-1.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/design-principle-22.html  
https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering-overview.html  
https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html  

<br>

#### Agrupe los datos entrantes usando reglas de IoT Core, antes de enviarlos a otros servicios de AWS

Una vez ingeridos, agrupar los datos de telemetría permite que esos lotes sean procesados o almacenados en bloque, lo que puede ser más eficiente.

Por ejemplo, puede agrupar los datos de mensajes de telemetría con Amazon Kinesis Data Firehose, antes de escribir en Amazon S3 en bloque. Escribir menos archivos más grandes de datos de telemetría de dispositivos en S3 es más eficiente que escribir numerosos archivos más pequeños. En este ejemplo, escribir y leer muchos archivos pequeños incurrirá en mayores costos de S3 para las operaciones de PUT y GET.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/cost-effective-resources.html

<a name="performance"></a>

## Consideraciones de Eficiencia de Rendimiento:

#### Equilibre la frecuencia y la cantidad de datos enviados desde sus dispositivos con las necesidades de su aplicación, y las limitaciones de hardware y red de su dispositivo

Considere con qué frecuencia su aplicación requiere que se envíen mensajes (datos) desde los dispositivos. *¿Requiere un flujo constante de mensajes pequeños (es decir, actualizaciones frecuentes)? ¿O su caso de uso admite agrupar mensajes durante un cierto intervalo antes de enviarlos?*

* Equilibre esto con las limitaciones de su dispositivo. Los dispositivos IoT pueden tener capacidad de procesamiento/local almacenamiento/energía de batería limitados, y conectarse a través de conexiones de red intermitentes o lentas. Por lo tanto, puede ser poco práctico conectarse con demasiada frecuencia (por ejemplo, agota la batería), y sin embargo, también puede haber una necesidad de conectarse con la suficiente frecuencia para no perder datos del dispositivo (por ejemplo, el almacenamiento local se llena y se sobrescribe).

* Esto informará la frecuencia de los mensajes de su dispositivo hacia la nube. Si su aplicación no requiere actualizaciones inmediatas de sus dispositivos, considere enviar con menos frecuencia para conservar el ancho de banda de la red y la energía de la batería.

También debe considerar si hay valor comercial en transmitir todos los datos sin procesar de sus dispositivos a la nube. *¿Puede resumir datos, eliminar valores duplicados, truncar o ignorar ciertas categorías para transmitir menos datos en general?*

* Esto informará si puede tomar medidas de procesamiento local para reducir la cantidad de mensajes y los tamaños de carga útil correspondientes, lo que puede ser útil con redes limitadas.

Si su hardware y caso de uso lo permiten:
* Determine qué datos necesitan ser transmitidos en primer lugar - tal vez solo hay unas pocas categorías que tienen valor, y puede filtrar el resto.
* Considere comprimir las cargas útiles y agrupar eventos en un solo mensaje antes de enviarlo a la nube, para una mayor eficiencia de transmisión.
* Realice procesamiento local para agregar puntos de datos y enviar los resultados, en lugar de los datos sin procesar.

Estas consideraciones también son importantes desde una perspectiva de [optimización de costos](#cost).

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/tradeoffs.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-19-3.html

<br>

#### Si usa el protocolo MQTT, determine el nivel óptimo de Calidad de Servicio (QoS) para publicar mensajes

AWS IoT Core soporta los niveles de Calidad de Servicio (QoS) 0 y 1 de MQTT.

QoS 0 enviará un mensaje 0 o más veces, por lo tanto, la entrega no está garantizada. Es el valor predeterminado sugerido en casos donde las conexiones se consideran generalmente confiables y cuando la falta de mensajes no es un problema para la aplicación IoT.

QoS 1 enviará un mensaje al menos una vez, y repetidamente hasta que sea reconocido. Debe usarse en situaciones donde se requiere entrega al menos una vez. Las compensaciones para la confiabilidad incluyen mayor sobrecarga, latencia y potencial de mensajes duplicados.

También vea: [Descripción general de métodos de conexión](#appendix) en el Apéndice.

##### Más información:
https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-19-2.html

<br>

#### Para aplicaciones que requieren procesamiento inmediato de la telemetría del dispositivo, procese los datos sin conexión en el Edge

En situaciones donde un dispositivo no está limitado por hardware, pero la conectividad de red sí lo está, soluciones de edge como AWS IoT Greengrass pueden usarse para procesar datos localmente y responder a eventos más rápidamente.

Por ejemplo, en un caso de uso industrial, el procesamiento local puede detectar y responder más rápidamente a eventos o condiciones particulares del equipo, en lugar de esperar a que los datos se envíen a la nube, se procesen de forma remota y se genere una alerta desde allí.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/tradeoffs.html


<a name="perf_localgateway"></a>
#### Considere que los dispositivos locales limitados interactúen con un gateway local

Si tiene un grupo de dispositivos locales altamente limitados (por ejemplo, sensores con almacenamiento local limitado o conectividad WAN) e instalados en un lugar particular (por ejemplo, una fábrica), un gateway local puede actuar como una ubicación de almacenamiento, agregador e intermediario hacia la nube.

Un gateway local puede almacenar, agrupar, manipular, enriquecer y procesar datos de otros dispositivos locales, antes de enviar datos relevantes a la nube en su nombre. Ejemplos incluyen el uso de AWS IoT Greengrass o AWS IoT SiteWise en casos de uso de equipos industriales.

Procesar (o preprocesar) datos en un gateway local puede resultar en respuestas más rápidas a eventos y en requisitos reducidos de procesamiento y cómputo para esos datos, una vez entregados a la nube.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-15-3.html

<br>

#### Use servicios gestionados para reducir su trabajo pesado no diferenciado

Los servicios gestionados eliminan el esfuerzo manual, la carga de mantenimiento y reducen la complejidad. Aprovecharlos dentro de su pipeline de ingesta y aplicación IoT ayudará a mejorar el rendimiento, la escalabilidad y la confiabilidad.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/selection.html

<br>

#### Desacople la ingesta del procesamiento con colas y flujos

Implementar **acoplamiento flexible** entre AWS IoT Core y los servicios downstream ayudará a evitar sobrecargar su aplicación si los volúmenes y tasas de ingesta son más altos que la capacidad de procesamiento actual, y facilita la escalabilidad de su aplicación IoT.

Use reglas de IoT para enviar datos a servicios de buffer y streaming como Amazon SQS, Amazon Kinesis y Amazon Managed Streaming para Apache Kafka (MSK). Estos servicios mantendrán los datos de manera segura, hasta que una aplicación downstream pueda procesarlos. 

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/ingestion-layer.html  
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-workload-architecture.html (See REL4)

<br>

#### Agrupe los datos entrantes usando reglas de IoT, antes de enviarlos a otros servicios de AWS

Una vez recibidos, agrupar los datos de telemetría permite que esos lotes sean procesados o almacenados en bloque, lo que puede ser más eficiente.

Por ejemplo, puede agrupar los datos de mensajes de telemetría con Amazon Kinesis Data Firehose, antes de escribir en Amazon S3 en bloque. Escribir menos objetos más grandes de datos de telemetría de dispositivos en S3 es más eficiente que escribir numerosos objetos más pequeños. Además:
* Si se requieren transformaciones o conversiones de los datos, podrían aplicarse de manera más eficiente al lote, antes de ser persistidos.
* Tener muchos objetos pequeños en S3 puede inflar el número de objetos en sus buckets.

Más generalmente, agrupar datos también puede ayudar a evitar posibles cuellos de botella de rendimiento o [cuotas de servicio](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html) con servicios downstream de AWS, por ejemplo, con la concurrencia de AWS Lambda.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/cost-effective-resources.html  
https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html

<br>

#### Monitoree su aplicación IoT para el rendimiento y para detectar posibles problemas

Monitoree continuamente su aplicación para evaluar su rendimiento y detectar indicaciones de posibles interrupciones.

Por ejemplo, asegúrese de que no esté alcanzando o acercándose a ninguna [cuota de servicio](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html) de AWS a medida que escala. Donde existan cuotas de servicio, profundice para entender cuáles son ajustables (límites suaves) y cuáles no (límites duros).

Aplique herramientas como Amazon CloudWatch para determinar los patrones, métricas y KPIs de referencia para su aplicación. Continúe monitoreando y rastreando esas métricas, y configure alarmas para notificarle según sea necesario.

Esta práctica se aplica a múltiples pilares, incluyendo Eficiencia de Rendimiento, Confiabilidad y Excelencia Operacional.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-18-1.html
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-foundations.html  
https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-23-3.html  

<br>

#### ¡Pruebe!

Realice pruebas a escala de producción para asegurarse de que toda su aplicación IoT, incluida la capa de ingesta, continúe funcionando y escalando como se espera, a medida que aumenta la carga.

Puede usar una aplicación simuladora para generar eventos a la escala adecuada.

Durante las pruebas, observe de cerca las métricas de rendimiento relevantes, incluidas aquellas que se relacionan con cualquier [cuota de servicio](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html).

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/design-principle-16.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-16-4.html  
https://docs.aws.amazon.com/iot/latest/developerguide/device-advisor.html  

<a name="reliability"></a>

-----
## Consideraciones de Confiabilidad:

#### Diseñe dispositivos para fallos y conectividad intermitente

Los dispositivos IoT pueden tener energía de batería limitada y conectarse a través de conexiones de red intermitentes o deficientes. Por lo tanto, los dispositivos pueden estar desconectados durante largos períodos de tiempo.

Para asegurarse de que su aplicación IoT pueda ingerir los datos de sus dispositivos, deberá diseñarlos para tolerar la conectividad intermitente. Haga esto almacenando datos importantes localmente hasta que se restablezca la conectividad, respetando las limitaciones de hardware (almacenamiento y energía). Por ejemplo, los SDK de AWS y AWS IoT Greengrass admiten el almacenamiento en búfer local de datos en disco mientras los dispositivos están desconectados.

Como se mencionó en [el pilar de Rendimiento](#perf_localgateway), también puede aprovechar un gateway local para aumentar los dispositivos altamente restringidos. Un gateway local puede almacenar, agrupar, manipular, enriquecer y procesar datos de otros dispositivos locales, antes de enviar datos relevantes a la nube en su nombre. Por ejemplo, utilizando AWS IoT Greengrass o AWS IoT SiteWise en casos de uso de equipos industriales.

Para situaciones en las que los dispositivos tienen dificultades para conectarse a la nube, implemente lógica de reintento y use aleatorización y retroceso exponencial para asegurarse de que su flota de dispositivos escalone el tiempo de sus conexiones, de modo que no todos intenten conectarse a la vez y generen un pico de tráfico prevenible.

Para mayor resiliencia, considere soportar múltiples métodos de conexión a la nube (por ejemplo, celular, wi-fi), y cambiar a un método de respaldo cuando sea necesario para enviar mensajes críticos.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-11-2.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-11-4.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-15-3.html  

<br>

#### Desacople la ingesta del procesamiento con colas y flujos

Implementar **acoplamiento flexible** entre AWS IoT Core y los servicios downstream ayudará a evitar la pérdida de datos en caso de que los servicios downstream no respondan. Además, este diseño evitará sobrecargar su aplicación si los volúmenes y tasas de ingesta son más altos que la capacidad de procesamiento actual, y facilita la escalabilidad de su aplicación IoT.

Use reglas de IoT para enviar datos a servicios de buffer y streaming como Amazon SQS, Amazon Kinesis y Amazon Managed Streaming para Apache Kafka (MSK). Estos servicios mantendrán los datos de manera segura, hasta que una aplicación downstream pueda procesarlos.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/ingestion-layer.html  
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-workload-architecture.html (See REL4)

<br>

#### Guarde los datos ingeridos en un almacenamiento duradero antes de procesarlos

Guardar los datos entrantes del dispositivo en un almacenamiento duradero (por ejemplo, Amazon S3) antes de procesarlos proporciona una copia de respaldo en caso de errores. También proporciona la opción de procesar los datos sin procesar de manera diferente en el futuro, si cambian sus necesidades.

Por ejemplo, durante la ingesta, una regla de AWS IoT puede enviar datos del dispositivo a Amazon Kinesis Data Firehose, que puede agrupar los datos y entregarlos a Amazon S3. Si elige aplicar transformaciones a los datos a través de Kinesis Firehose, también tiene la opción de persistir los datos sin procesar en su formato original en otra ubicación de S3, dándole una copia de respaldo sin modificar.

Dependiendo de su caso de uso, hay muchas otras opciones de almacenamiento duradero que puede usar, incluyendo Amazon EBS (si procesa con recursos de Amazon EC2), o servicios de bases de datos como Amazon DynamoDB, Amazon Timestream o Amazon Aurora, por nombrar algunos.

Si es necesario, considere copiar datos críticos a otra ubicación (Región de AWS o Zona de Disponibilidad, según corresponda) para fines de recuperación ante desastres.

También vea: [Use un data lake](#cost_datalake) en la sección de costos anterior.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-10-1.html

<br>

#### Use acciones de error para sus reglas de IoT

Si una acción de regla de AWS IoT experimenta un problema, por ejemplo, un servicio downstream no acepta datos de IoT Core, puede configurar **acciones de error** para mitigar. Las acciones de error se definen dentro de las reglas de IoT y solo ocurren si una acción de regla de IoT falla.

Puede aprovecharlas para generar alertas y prevenir la pérdida de datos durante una falla. Por ejemplo, puede enviar una alerta a través de un tema de SNS y guardar los datos del dispositivo en una ubicación duradera alternativa (como S3, SQS, Kinesis) para análisis o reintento futuro. Asegúrese de que su acción de error no escriba en el mismo servicio que la acción principal de la regla, para evitar que el mismo problema interrumpa la acción de error (por ejemplo, si se alcanzó una cuota de servicio).

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/failure-management.html  
https://docs.aws.amazon.com/iot/latest/developerguide/rule-error-handling.html

<br>

#### Monitoree su aplicación IoT para el rendimiento y para detectar posibles problemas

Monitoree continuamente su aplicación para evaluar su rendimiento y detectar indicaciones de posibles interrupciones.

Por ejemplo, asegúrese de que no esté alcanzando o acercándose a ninguna [cuota de servicio](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html) de AWS a medida que escala. Donde existan cuotas de servicio, profundice para entender cuáles son ajustables (límites suaves) y cuáles no (límites duros).

Aplique herramientas como Amazon CloudWatch para determinar los patrones, métricas y KPIs de referencia para su aplicación. Continúe monitoreando y rastreando esas métricas, y configure alarmas para notificarle según sea necesario.

Esta práctica se aplica a múltiples pilares, incluyendo Eficiencia de Rendimiento, Confiabilidad y Excelencia Operacional.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-18-1.html  
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-foundations.html  
https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-23-3.html  


<a name="security"></a>

----
## Consideraciones de Seguridad:

#### Asigne a cada dispositivo una identidad única y un certificado X.509

Es esencial que se establezca confianza entre sus dispositivos IoT y su aplicación IoT.

Sus dispositivos IoT deben tener cada uno una identidad única en AWS IoT, respaldada por un certificado X.509 único y confiable. Los certificados no deben compartirse. Esto permite una gestión de acceso detallada.

En caso de compromiso o retiro del dispositivo, la revocación del certificado específico del dispositivo permitiría el bloqueo selectivo del dispositivo afectado.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-1-1.html

<br>

#### Haga cumplir el acceso de privilegio mínimo para los temas MQTT

Para reducir el riesgo, haga cumplir el acceso de privilegio mínimo a sus temas MQTT.

Cree permisos granulares de IoT (es decir, políticas) que solo permitan a los dispositivos y aplicaciones acceder a los temas MQTT específicos que requieren. Por ejemplo, a cada dispositivo se le puede dar acceso a su propio tema MQTT, pero no a los de otros. Mientras tanto, su aplicación puede tener diferentes requisitos y puede necesitar acceso a los temas de muchos dispositivos para realizar su trabajo.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-1-2.html



<a name="operational"></a>

----
## Consideraciones de Excelencia Operacional:

#### Monitoree su aplicación IoT para el rendimiento y para detectar posibles problemas

Monitoree continuamente su aplicación para evaluar su rendimiento y detectar indicaciones de posibles interrupciones.

Por ejemplo, asegúrese de que no esté alcanzando o acercándose a ninguna [cuota de servicio](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html) de AWS a medida que escala. Donde existan cuotas de servicio, profundice para entender cuáles son ajustables (límites suaves) y cuáles no (límites duros).

Aplique herramientas como Amazon CloudWatch para determinar los patrones, métricas y KPIs de referencia para su aplicación. Continúe monitoreando y rastreando esas métricas, y configure alarmas para notificarle según sea necesario.

Esta práctica se aplica a múltiples pilares, incluyendo Eficiencia de Rendimiento, Confiabilidad y Excelencia Operacional.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-18-1.html  
https://docs.aws.amazon.com/wellarchitected/latest/framework/a-foundations.html  
https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-23-3.html  

<br>

#### Configure registros detallados para mejorar la solución de problemas y obtener información operativa

Puede habilitar el registro en AWS IoT para capturar más información sobre los mensajes a medida que llegan desde los dispositivos, pasan por el broker MQTT y el motor de reglas. Esto puede ser muy útil para fines de solución de problemas durante la ingesta, o para detectar proactivamente problemas emergentes que podrían afectar la salud de la aplicación.

Los registros se envían a Amazon CloudWatch Logs.

El nivel de verbosidad del registro es ajustable.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-23-3.html  
https://docs.aws.amazon.com/iot/latest/developerguide/configure-logging.html  
https://docs.aws.amazon.com/iot/latest/developerguide/cloud-watch-logs.html  

<a name="appendix"></a>

-----

## Apéndice: Consideraciones y recomendaciones adicionales relacionadas con la ingesta

<br>

### Descripción general de los métodos de conexión - Selección del enfoque correcto:

Conecte sus dispositivos a AWS IoT Core utilizando el método más apropiado para su caso de uso:

<table>
  <tr>
	<th>Opción</th>
	<th>Descripción</th>
	<th>Cuándo</th>
	<th>Comentarios</th>
  </tr>
  <tr>
    <td>AWS IoT Core con MQTT</td>
    <td>Use AWS IoT Core para capacidades de ingesta de datos y gestión de dispositivos, con el protocolo MQTT</td>
    <td>Sus dispositivos soportan MQTT</td>
    <td>
        <ul>
            <li>Soporta conexiones de larga duración</li>
            <li>Publicar y suscribirse</li>
            <li>Motor de reglas</li>
            <li>Niveles de QoS de MQTT 0 y 1 soportados</li>
        </ul>
    </td>
  </tr>
  <tr>
    <td>AWS IoT Core con HTTPS</td>
    <td>Use AWS IoT Core para ingesta de datos con el protocolo HTTPS</td>
    <td>Sus dispositivos no soportan MQTT, o prefieren HTTPS</td>
    <td>
        <ul>
            <li>Las conexiones no son de larga duración (sondeo)</li>
            <li>Capacidades solo de publicación (sin suscripción)</li>
			<li>Rules engine</li>
		</ul>
	</td>
  </tr>
  <tr>
    <td>Híbrido</td>
    <td>Los dispositivos se conectan a AWS IoT Core para la gestión, pero los datos se ingieren por otros medios</td>
    <td>Está ingiriendo cargas útiles de datos grandes que superan los 128KB (y no se pueden dividir), como video</td>
    <td>
        <ul>
            <li>Gestionar y controlar la flota de dispositivos a través de AWS IoT Core (usando MQTT)</li>
            <li>La ingesta de datos se realiza por otros medios, por ejemplo, Amazon Kinesis Video Streams, Amazon Kinesis Data Streams, Amazon MSK, Amazon SQS o Amazon API Gateway</li>
        </ul>
    </td>
  </tr>
  <tr>
    <td>Solución personalizada</td>
    <td>Conectar dispositivos e ingerir datos usando una solución completamente personalizada (no AWS IoT)</td>
    <td>Está ejecutando una solución propietaria o heredada que no depende de AWS IoT</td>
    <td>
        <ul>
            <li>Dispositivos IoT autogestionados</li>
            <li>AWS IoT Core no se utiliza</li>
            <li>Podría ingerir datos a través de una aplicación personalizada (por ejemplo, ejecutándose en Amazon EC2), u otros servicios de AWS (por ejemplo, Amazon Kinesis, Amazon MSK, Amazon SQS o Amazon API Gateway)</li>
        </ul>
    </td>
  </tr>
  <tr>
    <td>IoT Core con MQTT sobre Websockets</td>
    <td>Use AWS IoT Core para capacidades de ingesta de datos y gestión de dispositivos, con el protocolo MQTT sobre conexiones WebSockets</td>
    <td>Sus dispositivos ya usan, o hay una preferencia por WebSockets</td>
  </tr>
</table>


##### Más información:
https://docs.aws.amazon.com/iot/latest/developerguide/protocols.html

<br>

<br>

### Consideraciones Misceláneas del Edge

#### Mantenga la hora del dispositivo precisa en Tiempo Universal (UTC)

La hora precisa del dispositivo es importante para las marcas de tiempo de captura de datos y para fines de seguridad (por ejemplo, evaluar la validez de los certificados y, por lo tanto, la autenticación). Sin embargo, las baterías de los dispositivos IoT pueden descargarse y los relojes pueden desviarse con el tiempo. Como resultado, considere que sus dispositivos sincronicen su hora con una fuente externa precisa, como un servidor NTP, cuando sea posible.

Al estandarizar en Tiempo Universal (UTC) para sus dispositivos, puede asegurar la consistencia en toda su flota, independientemente de la ubicación física. Esto abstrae las zonas horarias o ajustes para el horario de verano a nivel del dispositivo.

##### Más información:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-12-1.html  
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/best-practice-16-3.html

<br>

#### Use IDs únicos para sus dispositivos IoT e incluya el ID con la carga útil de datos

Más allá del [valor de seguridad](#security) de tener un ID único para cada dispositivo, esto asegura que la fuente de los datos pueda ser identificada fácilmente y facilita el enriquecimiento de los datos con otra información que ya está almacenada o se conoce sobre el dispositivo.

<br>

#### Los dispositivos Edge deben generar un ID de evento secuencial para serializar cada evento

Si bien las marcas de tiempo son útiles para ordenar los datos recopilados o generados por los dispositivos IoT, es posible que múltiples elementos terminen con la misma marca de tiempo. Asignar un ID de evento secuencial a cada evento ayudará a determinar el orden correcto.

<br>

### Recursos Adicionales:

IoT Lens - AWS Well-Architected Framework:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens/welcome.html

IoT Lens Checklist:
https://docs.aws.amazon.com/wellarchitected/latest/iot-lens-checklist/overview.html

AWS Well-Architected Framework:
https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html

AWS IoT Core Developer Guide:
https://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html








