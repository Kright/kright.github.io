---
layout: page
title: "Мои заметки"
permalink: /index
---

Иногда пишу статьи на хабр, dtf или ещё куда-то. На всякий случай они сохранены тут. Ещё тут можно найти маленькие или не дописанные заметки.

{% for article in site.articles %}
* {{article.title}} -  {{article.url}}
{% endfor %}

{% for post in site.posts %}
* [{{post.title}}]({{post.url}})
{% endfor %}
