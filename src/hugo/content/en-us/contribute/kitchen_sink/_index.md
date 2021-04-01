---
title: "Kitchen Sink"
weight: 99
---

This page contains examples of all formatting and Hugo related shortcodes that can be used in an article.

### Multi-tab Content

Can be used to show the same example written in different languages, or content specific to different versions.

When using more than once on a page, make sure to set the `groupId` to be unique per set of content to render the first tab selection.

#### Code fence

{{< tabs groupId="code-fence">}}
{{% tab name="python" %}}

```python
print("Hello World!")
```

{{% /tab %}}
{{% tab name="java" %}}

```java
> print("Hello World!")
```

{{% /tab %}}
{{% tab name="bash" %}}

```Bash
echo "Hello World!"
```

{{% /tab %}}
{{< /tabs >}}

#### Release notes

{{< tabs groupId="release-notes">}}
{{% tab name="1.0.0" %}}
This was released in `1.0.0`:

- Initial deployment
  {{% /tab %}}

{{% tab name="1.1.0" %}}
This was released in `1.1.0`:

- Minor bug fix
- Minor new feature
  {{% /tab %}}

{{% tab name="2.0.0" %}}
This was released in `2.0.0`:

- Major update
- Something else of importance

{{% /tab %}}
{{< /tabs >}}
