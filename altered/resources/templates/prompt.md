{% extends "index.md" %}

{% block content %}

<context>
{% include "context.md" ignore missing %}
</context>


<user_prompt>
{% include "instructs_user_prompt.md" ignore missing %}
</user_prompt>


<INST>
{% include "instructs.md" ignore missing %}
</INST>

{% endblock %}