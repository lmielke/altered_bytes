{% extends "i_index.md" %}

{% block content %}

<context>
{% include "i_context.md" ignore missing %}
</context>


<user_prompt>
{% include "i_instructs_user_prompt.md" ignore missing %}
</user_prompt>


<INST>
{% include "i_instructs.md" ignore missing %}
</INST>

{% endblock %}