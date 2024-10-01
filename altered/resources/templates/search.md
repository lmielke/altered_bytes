{% extends "i_index.md" %}

{% block content %}

<context>
## {{ instructs.strats.method.data.name }}
{{ instructs.strats.method.data.description }}
{{ instructs.strats.method.data.example }}
</context>


<user_prompt>
    None
</user_prompt>

<INST>
{% include "i_instructs.md" ignore missing %}
</INST>

{% endblock %}