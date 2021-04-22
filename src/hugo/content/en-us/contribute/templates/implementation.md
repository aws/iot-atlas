---
title: "Implementation Template File"
weight: 20
summary: "Template for new provider-specific implementations of a general pattern."
---

Use the following text as the basis for new _implementations_ of provider-specific _patterns_. Create a new directory for the implementation under `src/hugo/content/en-us/implementations/PROVIDER` (replace `en-us` with other supported languages), then copy and paste the following content into a new file named `_index.html`.

```markdown
---
# replace PATTERN with the pattern this implementation addresses
title: "Pattern - Short Description"
# change weight to position in list
weight: 10
summary: "summary of the implementation"
---

Description of the implementation.

## Use Cases

List the use cases and persona-based stories for this implementation.

## Reference Architecture

Insert a reference architecture diagram or other representation of the implementation.

Define and describe the actors:

- _Actor 1_ is something
- _Actor 2_ is something

If there are flows or interactions, use numbers and a list to describe.

1. _Actor 1_ does something
1. _Actor 2_ responds to _Actor 1_

### Assumptions

Place any assumptions for the reader here.

## Implementation

This section goes through the specific steps on how this solution is implemented. It can be through code, processes, or other methods.

### Group 1

If there are multiple series or groups of steps, use the `###` or `h3` heading level to group.

### Group 2

Next group of implementation steps.

## Considerations

Every implementation should have one or more considerations. A consideration could be in how devices interact, error conditions that may arise, or other things a reader should consider when applying the implementation for their use.

### Consideration 1

Lorem ipsum dolor sit amet, exercitation id sit eiusmod culpa consectetur nulla et excepteur labore

### Consideration 2

Lorem ipsum dolor sit amet, proident mollit exercitation est commodo ea cillum magna anim adipisicing nulla proident duis aliquip tempor
```

Once saved, use the [local development and testing process]({{< ref "/contribute#validate-content" >}}) to review the following:

1. Your content appears under the _Implementations_ menu, under the provider section
1. The summary appears under the provider and pattern category, for example [_Implementations/AWS_]({{< ref "/implementations/aws" >}})
1. Your content is fully rendered properly
