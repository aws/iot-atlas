---
title: "accueil"
---

{{< atlas-logo >}}

# Bienvenue

Bienvenue sur le site IoT Atlas, où les voyages réussis utilisant l'Internet des appareils (IoT) reposent sur des cartes.

Les projets IoT les plus réussis ont des résultats commerciaux clairement définis. La grande majorité des projets IoT traversent différentes phases. Un prototype en premier lieu, puis un pilote suivi par la production limitée pour enfin arriver à la production dont le but est d'atteindre les résultats commerciaux identifiés à grande échelle. L'IoT Atlas soutient votre projet en expliquant pourquoi, comment et quels sont les architectures de référence IoT modernes les plus couramment utilisées.

## Aperçu

De nombreuses architectures IoT actuellement utilisées dans le monde ont été éprouvées mais restent peu connues.Les architectures proviennent souvent de domaines matures tels que _les réseaux de capteurs_, les architectures de _[système de contrôle](https://en.wikipedia.org/wiki/Control_system)_, les réseaux de _[machine à machine](https://en.wikipedia.org/wiki/Machine_to_machine)_ et le développement de _[système embarqué](https://en.wikipedia.org/wiki/Embedded_system)_. Mais le manque de visibilité de ces architectures matures pousse de nombreuses personnes à [réinventer la roue](https://en.wikipedia.org/wiki/Reinventing_the_wheel) pour leur solution, alors qu'elles ne le préfèrent pas. Pour compliquer davantage la situation pour les praticiens expérimentés, même lorsqu'une architecture de référence de longue date est connue, l'architecture doit souvent être mise à jour pour prendre en compte les concepts de développement du cloud.

L'IoT Atlas est une ressource pour les nouveaux et les praticiens de longue date de solutions Internet des appareils. Il met à jour et élargit les références d'architecture établies en supposant qu'aujourd'hui, la création de solutions «Internet des appareils» signifie presque toujours qu'un «cloud à très grande échelle est disponible» pour les praticiens qui créent chaque solution. Adopter la position selon laquelle le développement de solutions peut s'appuyer sur l'existence d'un cloud hyper-échelle n'implique pas que les architectures de l'IoT Atlas doivent être connectées pour fonctionner. Au lieu de cela, les architectures tentent de tirer parti de la force d'un parc d'appareils fonctionnant localement dans des environnements distants pendant de longues périodes **et** les forces du cloud à grande échelle, ubiquité mondiale et agilité de la solution. Les architectures peuvent ensuite être utilisées pour créer des solutions de haute qualité qui s'attendent à des pannes de réseau intermittentes, de longue durée ou principalement déconnectées comme une influence fondamentale de leurs composants conçus. Essentiellement, les architectures ci-dessous suivent la philosophie IoT selon laquelle _le traitement local de l'information complète le cloud_.

En partant de cette perspective, nous créons un atlas qui permet de comprendre même les considérations IoT les plus complexes. Ce serait formidable de vous joindre à nous et de [contribuer](https://github.com/aws/iot-atlas/blob/main/CONTRIBUTING.md) vos idées sur les architectures, considérations et des exemples pour ce voyage.

## Organisation

Chaque architecture tente de couvrir un concept, de bien le couvrir et, lorsque cela a du sens, de décrire comment l'architecture actuelle interagira avec d'autres architectures. Lorsqu'un nouveau concept est nécessaire pour mieux comprendre un design, le concept sera introduit juste à temps dans le design et également référencé dans le [glossaire]({{<ref "/glossary">}}).

Pour répondre à l'exigence de publication, une architecture complète de l'IoT atlas fournira une description simple en une ou deux phrases, une description concise du défi IoT abordé, un schéma architectural et un flux de processus simples non spécifiques au fournisseur, le profil communément intéressé et impacté par les capacités fournies par la conception et les considérations clés de mise en œuvre. Les considérations clés d'un design seront documentées dans l'IoT atlas lui-même et également par le biais de liens vers des ressources qui fournissent un contexte supplémentaire, comme des livres blancs, des articles de blog et du contenu vérifié sur Internet qui transmettent le mieux ce qui doit être pris en compte.

## Considérations sur le design

#### Niveau d'abstraction

Chaque design tente de décrire le schéma à un niveau d'abstraction qui incorpore autant de détails que possible, mais pas plus que nécessaire. Bien sûr, cet équilibre est difficile à atteindre et sera sûrement ajusté pendant la durée de cet effort.

Initialement, l'IoT Atlas décrira les design juste **ci-dessus** les détails des protocoles de communication, quel fournisseur ou quel langage de programmation pourrait être utilisé dans une implémentation. Par exemple, le design [Telemetry]({{<ref "/designs/telemetry">}}) est délibérément décris juste au-dessus des détails de [CoAP](http://coap.technology/), [MQTT](http://mqtt.org/), ou [AMQP](https://www.amqp.org/product/architecture) et pourtant quelqu'un de familier avec ces protocoles comprendrait toujours le concept du design sans aucune ou avec seulement une minorité de changement. Cette position est prise parce que les designs devraient bénéficier au plus grand nombre de personnes possible, quels que soient les détails de mise en œuvre spécifiques à l'outillage et au fournisseur. Cependant, des exemples spécifiques au fournisseur peuvent accélérer la compréhension pour ceux qui débutent. En tant que tel, l'IoT Atlas acceptera les implémentations de référence des designs, qui sont plus spécifiques que le pseudo-code peut être.

Il est peu probable que toutes les perspectives possibles puissent être incorporées, mais l'objectif de décrire les designs à ce niveau d'abstraction est conforme à l'intention principale d'aider les praticiens à comprendre le design à travers l'ensemble le plus large possible de solutions IoT.

#### Concepts clés

Les designs de l'IoT Atlas utiliseront le concept de [sujets de message]({{<ref "/glossary/vocabulary#sujet-du-message">}}) pour transmettre le flux détaillé des messages entre les appareils, entre les appareils et les composants, ou entre les composants de une solution IoT. Un sujet de message dans ce contexte doit être considéré comme une correspondance directe avec le concept pub / sub d'un sujet et comme un concept similaire aux URL partielles utilisées pour décrire le schéma demande/réponse supportant REST. En utilisant un concept unique pour décrire le sujet des messages utilisés dans un design, l'IoT atlas tente de décrire les concepts du design d'une manière plus simple.

Les designs de l'IoT Atlas supposent toutes qu'un appareil a toujours un `ID d'appareil` unique à la solution. Lorsque chaque appareil possède un ID unique de solution, chaque exemple spécifique est plus clair et une liste explicite d'appareil peut être utilisée pour implémenter un design d'une manière qui prend en charge plusieurs appareils. Lorsqu'une liste d'pbjets est cruciale pour le design, elle sera mentionnée.

#### Conventions

Enfin, chaque design suivra quelques conventions. Pour transmettre un exemple de données ou d'un concept lié au code, la police `monospace` sera utilisée en ligne; lorsqu'un mot ou un concept est crucial pour le design ou agit comme une définition juste à temps, une police de caractères **bold** sera utilisée; lorsqu'un bloc de code est le mieux à même de transmettre ou de renforcer un concept, ce bloc sera écrit au moins en tant que `pseudo-code` à espacement fixe. Au fil du temps, nous espérons contribuer et indexer des exemples de chaque design pour une variété de langues et de technologies.

## Équipe

À l'heure actuelle, les principaux responsables de l'IoT Atlas sont [Brett Francis](https://github.com/brettf),
[Gavin Adams](https://github.com/gadams999), et
[Craig Williams](https://github.com/typemismatch). Nous sommes ravis de diffuser ces designs dans le monde ici et sur [GitHub](https://github.com/aws/iot-atlas); ainsi, ensemble, nous pouvons accélérer ensemble les progrès dans le domaine de l'IoT.
