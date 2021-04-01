---
title: "Contribute"
---

TODO: complete as needed

This section provides guidance and resources on how to contribute to the IoT Atlas. It covers:

- [ ] Guidelines for content creation using Hugo
- [ ] Style guide
- [ ] Templates for different content types
- [ ] Process for creating and validating content locally

## Authoring new content

WHen creating new content, use the follow guidance:

1. A customized Hugo [Learn Theme](https://themes.gohugo.io//theme/hugo-theme-learn) is the basis for this site. Unless extended or called out below, all Learn Theme design content and shortcodes can be used. Additional features are listed below and shown in the [templates]({{< ref "/contribute/templates" >}}) folder, or in the [kitchen sink]({{< ref "/contribute/kitchen_sink" >}}) example that demonstrates all features.
1.

### Bundle Resources

If there are diagrams or other images related to your content, include and reference those from within the same directory as a [Page Bundle](https://gohugo.io/content-management/page-bundles/). For instance, a new _Pattern_ called _Foo_ would be structured like this:

```
Pattern/
  _index.md
  Foo/
    _index.md
    img1.png
    img2.png
```

Referencing images within `Pattern/Foo/_index.md` would look like this in markdown:

```markdown
Lorem ipsum dolor sit amet, consectetur adipiscing elit...

[Image One](img1.png)

sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
```
