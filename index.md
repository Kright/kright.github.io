---
layout: page
title: "Мои заметки"
permalink: /index
---

Иногда пишу статьи на хабр, на каждую уходит как минимум неделя моего времени. На всякий случай продублирую их тут - мало ли, что может случиться. Не хочется, чтобы они пропали.

{% for article in site.articles %}
* {{article.title}} -  {{article.url}}
{% endfor %}

{% for post in site.posts %}
* [{{post.title}}]({{post.url}})
{% endfor %}
