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
{%- endif%}


## Response Data and Format
{% include "i_instructs_io.md" ignore missing %}

## Your Task
{{ instructs.strats.your_task }}

Do not make any conversational comments!
Do not repeat any text or tags provided in this prompt!
Do not explain your reasoning unless specifically asked for!