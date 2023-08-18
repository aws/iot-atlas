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

1. A customized Hugo [Learn Theme](https://github.com/matcornic/hugo-theme-learn) is the basis for this site. Unless extended or called out below, all Learn Theme design content and shortcodes can be used. Additional features are listed below and shown in the [templates]({{< ref "/contribute/templates" >}}) folder, or in the [kitchen sink]({{< ref "/contribute/kitchen_sink" >}}) example that demonstrates all features.
1. If creating similar content that already exists, use an existing page as the basis for headings, style, and approach. You can also review the example style templates in this section.
1. Test content changes locally and only submit a [pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) once the validation passes successfully. Pull requests will not be merged with broken links or invalid Hugo references/code.

Following the steps below will ensure that any content or changes you make can be tested and validated prior to submitted a pull request. If you have any questions, please review and ask questions in the [discussions](https://github.com/aws/iot-atlas/discussions) section of the GitHub repository.

### Fork and Local Testing

To minimize installing local dependencies on your system, the only requirement is to have Docker installed locally. Also, the `make_hugo.sh` script is Linux/macOS (well, bash) specific, so for Microsoft Windows the commands would need to reviewed and changed. Setup your local environment by following these steps:

1. [Fork](https://github.com/aws/iot-atlas/fork) the repository in your GitHub account.
1. Optionally create a branch for your changes
1. From the `iot-atlas/src` directory, run `./make_hugo.sh -d` to start in local development mode.

{{%  notice note %}}
The first time doing this will locally build the docker container which will take 5-15 minutes. After that, the local `temporary/hugo-ubuntu` will be used to run hugo in a container
{{% /notice %}}

4. Verify you can open locally from the URL [http://localhost:1313/](http://localhost:1313/)

This final step starts a local server on port 1313 serving the rendered content. Every time you make and save a change, the local server will re-render and trigger your local browser to reload the page. If changes are not reflected, enter `CTRL+C` to stop the process and start `./make_hugo.sh -d` again. This can help when moving content or working with new directories

### Validate Content

Once you are happy with the new content, run `./make_hugo.sh -v`, which will _validate_ all the content is properly formatted, and that if you included any hyperlinks that they are valid. If errors are returned, correct and re-run.

When the message _\***\*\*\*\*\*** Validation completed successfully,_ is returned, validation is complete.

### Create a Pull Request

From GitHub, use the [pull request process](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) to create a pull request (PR) to the `aws/iot-atlas` repository. This will start a validation process under the [open pull requests](https://github.com/aws/iot-atlas/pulls?q=is%3Aopen+is%3Apr) again, and provide a message if the PR can be merged. If there are errors (red ❌ next to your PR), review the error, correct in _your_ forked repository, then commit the changes.

Once validation has completed, an IoT Atlas maintainer will review and either merge the content, or request changes or ask clarifying questions.

Once merged and content is live, you can delete the forked repository.

## Guidelines for Content Creation

This section covers both style and technical approaches to creating new content.

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
