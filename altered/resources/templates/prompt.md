{% extends "index.md" %}

{% block content %}

<context>

{% include "context.md" ignore missing %}
</context>

<user_prompt>
{%- include "user_prompt.md" ignore missing %}
</user_prompt>

<INST>
{%- include "instruct.md" ignore missing %}
</INST>

{% endblock %}