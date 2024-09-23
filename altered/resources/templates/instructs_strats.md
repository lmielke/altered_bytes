# 3. Instructions (INST)

## {{ instructs.strats.method.data.name }}
{{ instructs.strats.method.data.description }}
{{ instructs.strats.method.data.example }}

{%- if instructs.strats.method.data.task %}
## Objective
{{ instructs.strats.method.data.task }}
{% endif%}

{%- if instructs.strats.inputs %}
## Input Data
### {{ instructs.strats.inputs_header }}
{{ instructs.strats.inputs_intro }}
<sample>
{{ instructs.strats.inputs }}
</sample>

## Your Task
{{ instructs.strats.method.data.your_task }}
{% endif%}

## Response Layout and Format
{% if instructs.io %}
### Response Layout:
The following is a {{ instructs.strats.fmt.upper() }} template to be used for the expected LLM response. For clarity, comments have been added between the lines. 

<response_template>

{{ instructs.io }}

</response_template>

Return all entries shown in '<reponse_template>' combined into a single {{ instructs.strats.fmt.upper() }} string.
{% elif instructs.strats.fmt %}
Answer using plain {{ instructs.strats.fmt.upper() }} with no comments and no surrounding text!
{% else %}
Answer in plain text with no comments and no surrounding text!
{% endif%}