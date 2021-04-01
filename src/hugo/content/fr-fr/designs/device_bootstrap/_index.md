---
title: "Configuration de démarrage de l'appareil"
weight: 15
---

<!-- {{% synopsis-bootstrap %}} -->

Un appareil non enregistré devient enregistré et pleinement fonctionnel dans une solution IoT.

<!--more-->

## Défi

Les solutions IoT nécessitent que les appareils effectue une d'escalade de privilèges pour passer de zéro privilège à un appareil entièrement enregistré et opérationnel dans cette solution. Pour passer de _zéro_ privilège aux privilèges _complet_, il **devrait** y avoir des étapes séparées et planifiées. Chaque étape utilisée pour obtenir le privilège doit elle-même suivre l'approche du moindre privilège. De plus, il peut exister des systèmes d'identité et de privilèges qui doivent être intégrés à la solution IoT.

## Solution

Une solution IoT peut gérer les défis associés à la configuration initiale d'un appareil en déconstruisant ces défis en un processus s'appuyant sur deux concepts distincts: une _autorité d'enregistrement_ et un _escalateur de privilèges_.

Une **autorité d'enregistrement** est le composant qui valide les certificats, jetons ou informations d'identification partagés reçus de l'appareil, puis renvoie les informations d'identification de la solution à utiliser pour l'appareil. Une autorité d'enregistrement sera au moins un ensemble de politiques dictant la capacité des appareils non-enregistrés à s'abonner ou à publier sur des sujets définis sur le serveur.

Un **escalator de privilèges** permet à un appareil avec des informations d'identification de courte durée et des privilèges inférieurs de partager plus d'attributs sur lui-même ou de présenter un comportement approprié avant d'obtenir des privilèges plus élevés dans la solution. Une étape distincte d'escalade de privilèges permet également d'injecter l'approbation humaine dans le processus d'augmentation de privilèges, si la solution l'exige.

Bien qu'il existe des situations où une implémentation peut combiner l'enregistrement avec la possibilité d'obtenir des privilèges entièrement augmentés, en décomposant les défis comme cela est fait dans ce design, chaque défi peut être traité de manière distincte, en utilisant des systèmes nouveaux ou existants.

Le design Configuration de démarrage de l'appareil illustrée dans le diagramme suivant peut fournir cette fonctionnalité.

![Configuration initiale de l'appareil](bootstrap.png) ([PPTx](/iot-atlas-patterns.pptx))

### Numéros du diagramme

1. L'appareil s'enregistre auprès de l'autorité d'enregistrement en utilisant des informations d'identification partagées ou un jeton.
2. L'autorité d'enregistrement valide l'authenticité des informations d'identification ou du jeton partagés, enregistre l'appareil et renvoie les informations d'identification de courte durée à l'appareil.
3. L'appareil utilise les informations d'identification de courte durée pour contacter l'escalateur de privilèges et partager plus d'informations sur lui-même.
4. L'escalateur de privilèges détermine le type d'appareil et détermine si l'appareil doit être autorisé dans la solution IoT. Si l'appareil est autorisé, l'escalateur de privilèges renvoie des informations d'identification de longue durée, telles que des certificats associés à des privilèges correspondant à l'objectif de l'appareil dans la solution IoT.
5. L'appareil utilise les privilèges de longue durée pour s'abonner et publier sur le [sujet du message]({{<ref "/glossary/vocabulary#sujet-du-message">}}) de l'appareil via le point de terminaison du protocole du serveur.

## Considérations

Lors de la mise en œuvre de ce design, tenez compte des questions suivantes:

#### Le processus de fabrication de l'appareil crée-t-il et place-t-il le jeton initial sur l'appareil?

Si **non**, alors l'appareil doit disposer d'un mécanisme pour recevoir un jeton sécurisé ou un [certificat](https://en.wikipedia.org/wiki/Public_key_certificate) après la fabrication de l'appareil. Un tel mécanisme pourrait impliquer la configuration d'un appareil via une connexion Bluetooth Low Energy ([BLE](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy)) à partir d'une application mobile. Cela présente l'avantage de pouvoir associer immédiatement un appareil à un client pendant qu'il est connecté à une application mobile.

Si **oui - avec jeton / informations d'identification partagées**, dans ce cas il est important que le jeton initial ou les informations d'identification partagées soient utilisés pour activer uniquement les privilèges minimaux nécessaires pour s'enregistrer auprès de la solution. Une fois que l'autorité d'enregistrement a validé le jeton initial ou les informations d'identification partagées, les autres étapes de ce design doivent être suivies.

Si **oui - avec certificat**, l'appareil peut être fabriqué de manière sécurisée et le besoin d'une autorité d'enregistrement peut être réduit s'il n'est pas complètement supprimé. C'est facile à dire et difficile à réaliser car de nombreux processus de fabrication sont délibérément déconnectés du cloud. Quoi qu'il en soit, étant donné que la solution peut avoir une étape entière supprimée lorsque les clés sont introduites par le fabricant, l'expérience client et la simplicité globale du système en bénéficieront.

#### Comment les clients sont-ils associés à leurs appareils?

Dans presque tous les cas, lorsque les appareils sont provisionnés, nous devons associer l'appareil à un client ou à un profil d'appareil au sein d'un système établi. Cela implique la collecte d'informations supplémentaires sur l'appareil pour terminer l'enregistrement de l'appareil. La collecte de ces informations supplémentaires peut être accomplie avec un ou une combinaison des éléments suivants:

- Les appareils sont provisionnés pendant le processus de fabrication avec des [certificats](https://en.wikipedia.org/wiki/Public_key_certificate) et ces certificats peuvent être pré-associés à un profil d'appareil. Ceci est courant pour les solutions avec de grandes flottes d'appareils connus.
- Les appareils signalent leur modèle et leurs numéros de série lors de leur communication avec l'autorité d'enregistrement, ces informations peuvent être pré-associés sur un profil d'appareil.
- Les appareils utilisent BLE ou une autre forme de communication locale pour recevoir des informations sur leur identité, comme un profil client. La gestion de ces informations via une application mobile est la forme la plus courante d'approvisionnement des appareils. L'utilisation de la communication locale peut être couplée à l'installation de certificats pendant la fabrication, permettant à la fois l'association du client et le processus d'enregistrement en une seule étape.

#### Utilisez-vous des certificats pour vos appareils?

Bien que l'idée d'essayer de provisionner chaque appareil dans une solution avec un certificat puisse être intimidante, c'est de loin le moyen le plus sûr de provisionner des appareils. Il est important d'établir une authentification mutuelle pour empêcher les menaces telles que les attaques [man-in-the-middle](https://en.wikipedia.org/wiki/Man-in-the-middle_attack). Lors du démarrage de vos appareils, les certificats doivent toujours être votre premier choix pour l'identité de l'appareil.

#### L'autorité d'enregistrement doit-elle prendre en charge l'intégration des autorisations personnalisées avec une solution client existante?

Si **oui**, l'étape de l'autorité d'enregistrement du design peut être implémentée à l'aide d'une interface de programmation d'application ([API](https://en.wikipedia.org/wiki/Application_programming_interface)) devant une solution client existante. Cette API peut ensuite effectuer le travail de l'autorité d'enregistrement tout en tirant parti de la solution existante du client.

## Exemple

    <scenario à remplir>
