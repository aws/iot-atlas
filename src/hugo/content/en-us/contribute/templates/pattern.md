---
title: "Pattern Template File"
weight: 10
summary: "Template for new general patterns."
---

Use the following text as the basis for new _patterns._ Create a new directory for the pattern under `src/hugo/content/en-us/patterns` (replace `en-us` with other supported languages), then copy and paste the following content into a new file named `_index.html`.

```markdown
---
title: "Name of the Pattern"
# Select a weight to position in the pattern list (this comment can be removed)
weight: 10
summary: "A short summary that will be used to describe the pattern on the summary page."
---

A short summary of the pattern, this will be used to describe the pattern on the summary page.

## Challenge

Describe the challenge this pattern addresses.

## Solution

Describe the solution using diagrams, process flows, or other means with numbered steps. Review the Contribute section for guidelines for approved diagrams, and place the diagram files in the same directory as this file.

### Diagram Steps

1. For each step, go into detail what occurs
1. Then for the next step(s), their detail

## Considerations

Describe what an implementor should consider when using this pattern.

### Use a level 3 header for each question

Then for each question or consideration, and answer or details for it.

### This is an example of a second questions

## Examples

To illustrate the pattern, create a sub-section for each

### Describe the example

Explain the example in greater detail

### Describe a second example

And the second examples details.
```

Once saved, use the [local development and testing process]({{< ref "/contribute#testing-process" >}}) to review the following:

1. Your content appears under the _Patterns_ menu
1. The summary appears in the [_Patterns_]({{< ref "/patterns" >}}) list
1. Your content is fully rendered properly
