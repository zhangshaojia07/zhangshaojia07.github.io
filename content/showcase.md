+++
author = "Shaojia"
title = "Showcase"
date = "2026-02-06T20:31:17+08:00"
tags = []
description = "Sample article showcasing basic styling and formatting for HTML elements."
showFullContent = false
hideComments = false
Toc = true
+++

This article offers a sample of basic Markdown syntax that can be used in Hugo content files, also it shows whether basic HTML elements are decorated with CSS in a Hugo theme.
<!--more-->

## Headings

# H1
## H2
### H3
### H4
#### H5
##### H6

## Images

![Terminal Theme Preview](/img/terminal-theme.png)

### Figure with a caption

{{< figure src="/img/terminal-theme.png" alt="Terminal Theme Preview" position="center" caption="Terminal Theme Preview" captionPosition="center" >}}

## Blockquotes

The blockquote element represents content that is quoted from another source, optionally with a citation which must be within a `footer` or `cite` element, and optionally with in-line changes such as annotations and abbreviations.

### Blockquote without attribution

> Tiam, ad mint andaepu dandae nostion secatur sequo quae.
> **Note** that you can use *Markdown syntax* within a blockquote.

### Blockquote with attribution

> Don't communicate by sharing memory, share memory by communicating.<br>
> — <cite>Rob Pike[^1]</cite>

[^1]: The above quote is excerpted from Rob Pike's [talk](https://www.youtube.com/watch?v=PAAkCSZUG1c) during Gopherfest, November 18, 2015.

## Buttons and links

<button>Button</button>
<a href="">Link</a>
<a href="" class="button inline">Link</a>

## Tables

Tables aren't part of the core Markdown spec, but Hugo supports supports them out-of-the-box.

   Name | Age
--------|------
    Bob | 27
  Alice | 23

### Inline Markdown within tables

| Italics   | Bold     | Code   |
| --------  | -------- | ------ |
| *italics* | **bold** | `code` |

## Forms

<fieldset>
  <input type="text" placeholder="Type something" /><br />
  <input type="number" placeholder="Insert number" /><br />
  <input type="text" value="Input value" /><br />
  <select>
    <option value="1">Option 1</option>
    <option value="2">Option 2</option>
    <option value="3">Option 3</option>
  </select><br />
  <textarea placeholder="Insert a comment..."></textarea><br />
  <input type="checkbox" /> I understand<br />
  <button type="submi">Submit</button>
</fieldset>

## Code Blocks

### Code block with backticks

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Example HTML5 Document</title>
</head>
<body>
  <p>Test</p>
</body>
</html>
```

### Code block indented with four spaces

    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Example HTML5 Document</title>
    </head>
    <body>
      <p>Test</p>
    </body>
    </html>

### Code block with Hugo's internal highlight shortcode

{{< highlight html >}}
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Example HTML5 Document</title>
</head>
<body>
  <p>Test</p>
</body>
</html>
{{< /highlight >}}

### Code block with custom built-in `{{ < code > }}` shortcode

{{< code title="Hey, this is a code block title" language="css" >}}
pre {
  background: #1a1a1d;
  padding: 20px;
  border-radius: 8px;
  font-size: 1rem;
  overflow: auto;

  @media (--phone) {
    white-space: pre-wrap;
    word-wrap: break-word;
  }

  code {
    background: none !important;
    color: #ccc;
    padding: 0;
    font-size: inherit;
  }
}
{{< /code >}}

## List Types

### Ordered List

1. First item
2. Second item
3. Third item

### Unordered List

* List item
* Another item
* And another item

### Nested list

* Fruit
  * Apple
  * Orange
  * Banana
* Dairy
  * Milk
  * Cheese
  
## LaTeX

Using MathJax engine.

$$\LaTeX$$

$$ \int_{0}^{\infty}e^{-x}\text{ d}x $$

\[
  \text{why are you still there?}
\]

I have \(e^{\pi\text{i}}+1\) ideas.

## Other Elements — abbr, sub, sup, kbd, mark

<abbr title="Graphics Interchange Format">GIF</abbr> is a bitmap image format.

H<sub>2</sub>O

X<sup>n</sup> + Y<sup>n</sup> = Z<sup>n</sup>

Press <kbd>CTRL</kbd>+<kbd>ALT</kbd>+<kbd>Delete</kbd> to end the session.

Most <mark>salamanders</mark> are nocturnal, and hunt for insects, worms, and other small creatures.
