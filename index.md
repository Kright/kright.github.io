---
layout: page
title: "kright.github.io"
permalink: /index
---

## Мои заметки

{% for post in site.posts %}
* [{{post.title}}]({{post.url}})
{% endfor %}
