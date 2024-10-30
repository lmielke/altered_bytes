## Description: {{ instructs.strats.name }}
{{ instructs.strats.description }}

{%- if instructs.strats.example %}
## Strategy Example
{{ instructs.strats.example }}
{%- endif %}

## Strategy Objective
{{ instructs.strats.objective }}

{%- if instructs.strats.inputs_data %}
## {{ instructs.strats.inputs_header }}
{{ instructs.strats.inputs_intro }}
<!-- <{{ instructs.strats.inputs_tag }}> -->
{{ instructs.strats.inputs_data }}
<!-- </{{ instructs.strats.inputs_tag }}> -->
{% endif%}

## Response Layout and Format:
{%- include "i_instructs_io.md" ignore missing %}

## Your Task
{{ instructs.strats.your_task }}
Your answer must have between {{ instructs.strats.expected_words[0] }} and {{ instructs.strats.expected_words[1] }} words.
