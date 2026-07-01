---
title: "Archivage de télémétrie"
weight: 85
---

<!-- {{< synopsis-archiving >}} -->

Les mesures d'un appareil sont enregistrées et mises à disposition pour une utilisation dans leur forme originale ou modifiée.

<!--more-->

## Défi

Afin de fournir des informations pertinentes, les solutions IoT doivent prendre en charge l'analyse en temps réel, en mode groupé et prédictif des informations générées par la solution. Étant donné que chaque mode d'analyse est mieux informé lors de l'exploitation des données historiques _et_ que les futures approches d'analyse peuvent ne pas encore être comprises, les solutions IoT doivent archiver les données d'une manière aussi flexible que possible pour répondre aux besoins futurs.

## Solution

Les solutions IoT garantissent qu'une entreprise puisse obtenir la collection d'informations la plus récente et la plus évolutive en stockant les données brutes des capteurs non traités de manière à prendre en charge la relecture dans l'ordre de ces échantillons bruts. La capacité de stockage et de relecture devrait faire apparaître les échantillons bruts historiques presque comme si les échantillons arrivaient dans la séquence ordonnée dans le temps normal d'échantillons non historiques.

Le design d'archivage de télémétrie illustrée dans le diagramme suivant peut fournir cette fonctionnalité.

![Architecture d'archivage de télémétrie](archiving.png) ([PPTx](/iot-atlas-patterns.pptx))

### Numéros du diagramme

1. L'appareil obtient un point de mesure à partir d'un capteur fonctionnant dans un environnement éloigné de la solution IoT.
2. L'appareil publie un message avec le sujet `telemetry/deviceID` contenant le point de mesure. Ce message est envoyé via un protocole de transport à un point de terminaison de protocole mis à disposition par le serveur.
3. Le serveur peut ensuite appliquer une ou plusieurs [règles]({{<ref "/glossary/vocabulary#règle">}}) aux messages afin d'effectuer un routage à granularité fine sur tout ou partie des [messages]( {{<ref "/glossary/vocabulary#message">}}) contenant les données de mesure. Ces règles étendent les messages vers au moins un chemin de traitement **`(4)`** et un chemin de stockage brut **`(5)`**
4. Le chemin de traitement des messages effectue les calculs fondamentaux nécessaires aux autres composants de la solution et stocke les résultats traités.
5. Le chemin de stockage des messages bruts enregistre le message brut d'origine d'une manière prenant en charge la relecture dans l'ordre des messages d'origine.
6. À un moment donné dans le futur, un composant peut lire des messages bruts à un moment donné et relire ces messages sur le sujet `telemetry/deviceID/replay`. La solution traite les messages rejoués si nécessaire.

## Considérations

Lors de la mise en œuvre de cet design, tenez compte des questions suivantes:

#### La relecture des enregistrements est-elle requise pour le traitement en aval?

Dit simplement **oui**. La plupart des solutions doivent supposer que la réponse à cette question est "**oui**", car la relecture des données brutes des capteurs non traités permet à la solution IoT de prendre en charge l'évolution des exigences à travers:
  - les mises à jour des calculs fondamentaux qui permettent une analyse performante des données historiques,
  - la création de nouveaux types d'enregistrements traités,
  - l'implémentation de nouvelles fonctionnalités inattendues, et
  - la création de perspectives client fondamentalement nouvelles pour les données.

Un exemple de cette considération est [ci-dessous](#exemple-de-prise-en-compte-des-données-de-relecture).

#### Est-il important de garantir l'ordre des messages enregistrés?

Si **oui**: `Détails à fournir`

Si **non**: `Détails à fournir`

## Exemples

#### Exemple de prise en compte des données de relecture

Un site physique est mesuré sur l'énergie électrique ([kWh](https://en.wikipedia.org/wiki/Kilowatt_hour)) utilisée. Des capteurs d'énergie sont échantillonnés toutes les 30 secondes et les échantillons sont rapportés dans la solution une fois par minute. À mesure que les messages bruts et non traités arrivent, ils sont stockés et un processus de "moyenne sur 15 minutes" qui calcule automatiquement la moyenne sur 15 minutes de l'énergie mesurée utilisée. Les résultats calculés sont stockés sous forme d'enregistrements dans le référentiel d'enregistrements traités de la solution. Ces nouveaux enregistrements traités sont ensuite utilisés par des processus analytiques supplémentaires et l'interface utilisateur de la solution IoT.

À une date ultérieure, il est clair que les utilisateurs de la solution souhaitent également des enregistrements traités qui affichent l'énergie maximale utilisée toutes les 5 minutes. Pour offrir cet avantage, un nouveau processus "5 minutes maximum" est mis en œuvre. Ce nouveau processus rejoue les enregistrements bruts historiques non traités et calcule le maximum de 5 minutes sur chaque intervalle historique. Une fois terminé, chaque résultat calculé est stocké en tant que nouveau type d'enregistrement traité.

Sans la rétention des échantillons bruts, la solution se limiterait à effectuer uniquement des calculs sur les données qui arrivent après la mise en œuvre de la fonction "5 minutes maximum" dans la solution. Plus important encore, sans les échantillons bruts d'origine, les utilisateurs ne seraient pas en mesure d'analyser le site physique à l'aide de la fonctionnalité de 5 minutes, avant le moment où la fonctionnalité a été mise en œuvre.
