---
title: "Plantilla de Implementación"
weight: 20
summary: "Plantilla para nuevas implementaciones específicas de un proveedor de un patrón general."
---

Use el siguiente texto como base para nuevas _implementaciones_ específicas de un proveedor. Cree un nuevo directorio para la implementación bajo `src/hugo/content/es-es/implementations/PROVEEDOR`, luego copie y pegue el siguiente contenido en un nuevo archivo llamado `_index.md`.

```markdown
---
title: "Patrón - Descripción Corta"
weight: 10
summary: "Resumen de la implementación"
---

Descripción de la implementación.

## Casos de Uso

Liste los casos de uso e historias basadas en personas para esta implementación.

## Arquitectura de Referencia

Inserte un diagrama de arquitectura de referencia u otra representación de la implementación.

Defina y describa los actores:

- _Actor 1_ es algo
- _Actor 2_ es algo

Si hay flujos o interacciones, use números y una lista para describir.

1. _Actor 1_ hace algo
1. _Actor 2_ responde a _Actor 1_

### Suposiciones

Coloque cualquier suposición para el lector aquí.

## Implementación

Esta sección describe los pasos específicos de cómo se implementa esta solución.

### Grupo 1

Si hay múltiples series o grupos de pasos, use el encabezado `###` o `h3` para agrupar.

### Grupo 2

Siguiente grupo de pasos de implementación.

## Consideraciones

Cada implementación debe tener una o más consideraciones.

### Consideración 1

Lorem ipsum dolor sit amet, descripción de la consideración.

### Consideración 2

Lorem ipsum dolor sit amet, descripción de la segunda consideración.
```

Una vez guardado, use el [proceso de desarrollo local y pruebas]({{< ref "/contribute#validar-contenido" >}}) para revisar lo siguiente:

1. Su contenido aparece bajo el menú de _Implementaciones_, bajo la sección del proveedor
1. El resumen aparece bajo el proveedor y categoría del patrón
1. Su contenido se renderiza correctamente
