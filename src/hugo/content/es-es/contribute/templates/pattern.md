---
title: "Plantilla de Patrón"
weight: 10
summary: "Plantilla para nuevos patrones generales."
---

Use el siguiente texto como base para nuevos _patrones_. Cree un nuevo directorio para el patrón bajo `src/hugo/content/es-es/patterns` , luego copie y pegue el siguiente contenido en un nuevo archivo llamado `_index.md`.

```markdown
---
title: "Nombre del Patrón"
weight: 10
summary: "Un resumen corto que se usará para describir el patrón en la página de resumen."
---

Un resumen corto del patrón, esto se usará para describir el patrón en la página de resumen.

## Desafío

Describa el desafío que este patrón aborda.

## Solución

Describa la solución usando diagramas, flujos de proceso u otros medios con pasos numerados.

### Pasos del Diagrama

1. Para cada paso, detalle lo que ocurre
1. Luego para los siguientes pasos, sus detalles

## Consideraciones

Describa lo que un implementador debe considerar al usar este patrón.

### Use un encabezado nivel 3 para cada pregunta

Luego para cada pregunta o consideración, una respuesta o detalles.

## Ejemplos

Para ilustrar el patrón, cree una sub-sección para cada uno.

### Describa el ejemplo

Explique el ejemplo con mayor detalle.
```

Una vez guardado, use el [proceso de desarrollo local y pruebas]({{< ref "/contribute#validar-contenido" >}}) para revisar lo siguiente:

1. Su contenido aparece bajo el menú de _Patrones_
1. El resumen aparece en la lista de [_Patrones_]({{< ref "/patterns" >}})
1. Su contenido se renderiza correctamente
