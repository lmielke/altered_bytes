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

<{{ instructs.strats.strat_tag }}>
{{ instructs.strats.inputs }}
</{{ instructs.strats.strat_tag }}>

## Your Task
{{ instructs.strats.method.data.your_task }}
{% endif%}

## Response Layout and Format
{% if instructs.io %}
### Response Layout:
The following is a {{ instructs.strats.fmt.upper() }} template to be used for the expected LLM response. For clarity, comments {{ instructs.strats.fmt_comment }} have been added between the lines.

<response_template>

{{ instructs.io }}

</response_template>

Return all entries shown in '<reponse_template>' combined into a single {{ instructs.strats.fmt.upper() }} string. Your response should be shorter than {{ instructs.default_max_words }} words. Do NOT include comments {{ instructs.strats.fmt_comment }} or surrounding text!
{% elif instructs.strats.fmt %}
Answer using {{ instructs.strats.fmt.upper() }}! Do not include comments or surrounding text!
{% else %}
Answer in plain text! Do not include conversational text!
{% endif%}