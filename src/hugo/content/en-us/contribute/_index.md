---
title: "Contribute to the Atlas"
---

This section provides guidance and resources on how to contribute to the IoT Atlas. It covers:

- Authoring and testing new content
- Guidelines for content creation using Hugo
- Templates for different content types

Following these guidelines helps ensure the consistency of the Atlas from page to page.

## Authoring new content

When creating new content, use the follow guidance:

1. A customized Hugo [Learn Theme](https://themes.gohugo.io//theme/hugo-theme-learn) is the basis for this site. Unless extended or called out below, all Learn Theme design content and shortcodes can be used. Additional features are listed below and shown in the [templates]({{< ref "/contribute/templates" >}}) folder, or in the [kitchen sink]({{< ref "/contribute/kitchen_sink" >}}) example that demonstrates all features.
1. If creating similar content that already exists, use an existing page as the basis for headings, style, and approach. You can also review the example style templates in this section.
1. Test content changes locally and only submit a [pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) once the validation passes successfully. Pull requests will not be merged with broken links or invalid Hugo references/code.

Following the steps below will ensure that any contetn pr changes you make can be tested and validated prior to submitted a pull request. If you have any questions, please review and ask questions in the [discussions](https://github.com/aws/iot-atlas/discussions) section of the GitHub repository.

### Pre-requisites

To reduce installing dependencies, the main requirement is to have Docker installed locally. Also, the `make_hugo.sh` script is Linux/macOS (well, bash) specific, so for Microsoft Windows the commands would need to reviewed and changed.

### Testing Process

1. Once you are ready to start creating content, run the developer mode which will run Hugo locally in fast render mode.

   ```bash
   ./make_hugo.sh -d
   ```

1. This starts a local server on port 1313 serving the rendered content. The default URL is `http://localhost:1313` and will show _most_ content with the exception of rendered images from AsciiDoc or PlantUML. To see this content, fully generate the content and view locally from a web browser opening `src/hugo/public/index.html`.
1. Every time you make and save a change, the local server will re-render and trigger your local browser to reload the page. If changes are not reflected, enter `CTRL+C` to stop the process and start `./make_hugo.sh -d` again.

Once you have completed development, run `./make_hugo.sh` without any arguments to have it fully generate and validate the content. Once successful, you can commit and perform a pull requests.

## Guidelines for Content Creation

## Hugo and Theme Details

This sections covers structure and use of more complex pages and use of short codes. This site is based off of the [Hugo Learn Theme](https://github.com/matcornic/hugo-theme-learn). All content and shortcodes for that theme are available for use here. 

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
