## Description: {{ instructs.strats.name }}
{{ instructs.strats.description }}

## Example
{{ instructs.strats.example }}

## Objective
{{ instructs.strats.objective }}

{%- if instructs.strats.inputs_data %}
## {{ instructs.strats.inputs_header }}
{{ instructs.strats.inputs_intro }}

### Input Data
<!-- <{{ instructs.strats.inputs_tag }}> -->
{{ instructs.strats.inputs_data }}
<!-- </{{ instructs.strats.inputs_tag }}> -->
{% endif%}

{%- if instructs.io %}
## Response Data and Format
{% include "i_instructs_io.md" ignore missing %}
{% endif%}

## Your Task
{{ instructs.strats.your_task }}
