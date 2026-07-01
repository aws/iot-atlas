---
title: "Kitchen Sink"
weight: 99
---

Esta página contiene ejemplos de todo el formato y shortcodes relacionados con Hugo que se pueden usar en un artículo.

### Contenido Multi-pestaña

Se puede usar para mostrar el mismo ejemplo escrito en diferentes lenguajes, o contenido específico para diferentes versiones.

Cuando use más de una vez en una página, asegúrese de establecer el `groupId` como único por conjunto de contenido para renderizar la primera selección de pestaña.

#### Bloque de código

{{< tabs groupId="code-fence">}}
{{% tab name="python" %}}

```python
print("¡Hola Mundo!")
```

{{% /tab %}}
{{% tab name="java" %}}

```java
System.out.println("¡Hola Mundo!");
```

{{% /tab %}}
{{< /tabs >}}

### Aviso

Un aviso se utiliza para informar o resaltar algo al lector.

{{% notice note %}}
Esto es una nota informativa.
{{% /notice %}}

{{% notice warning %}}
Esto es una advertencia.
{{% /notice %}}

{{% notice tip %}}
Esto es un consejo útil.
{{% /notice %}}

### Expandir

Se usa para contenido colapsable.

{{%expand "Haga clic para expandir" %}}
Contenido oculto que se revela al hacer clic.
{{% /expand %}}
