{% extends "i_index.md" %}

{% block content %}

<context>
## {{ instructs.strats.name }}
{{ instructs.strats.description }}
{{ instructs.strats.example }}
</context>


<user_prompt>
    None
</user_prompt>

<INST>
{% include "i_instructs.md" ignore missing %}
</INST>

{% endblock %}