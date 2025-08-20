## Description: {{ instructs.strats.name }}
{{ instructs.strats.description }}

{%- if instructs.strats.example %}
## Task Example
{{ instructs.strats.example }}
{%- endif %}

## Task Objective
{{ instructs.strats.objective }}

{%- if instructs.strats.strat_input_data %}
{%- if instructs.strats.inputs_header %}
## {{ instructs.strats.inputs_header }}
{{ instructs.strats.inputs_intro }}
<!-- <{{ instructs.strats.inputs_tag }}> -->
{{ instructs.strats.strat_input_data }}
<!-- </{{ instructs.strats.inputs_tag }}> -->
{% endif%}
{% endif%}

## Response Layout and Format:
{%- if instructs.io %}
{% include "i_instructs_io.md" ignore missing %}
{%- else %}
{% include "i_io_default_fmt.md" ignore missing %}
{% endif%}

## Your Task
{{ instructs.strats.your_task }}
{%- if instructs.strats.expected_words[1] and instructs.strats.expected_words[1] != 0 %}
Your answer must have between {{ instructs.strats.expected_words[0] }} and {{ instructs.strats.expected_words[1] }} words.
{% endif%}
