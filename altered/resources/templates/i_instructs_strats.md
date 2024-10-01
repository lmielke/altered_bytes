{%- if instructs.strats.method.data.task %}
## Objective
{{ instructs.strats.method.data.task }}
{%- endif%}

{%- if instructs.strats.inputs %}

## {{ instructs.strats.inputs_header }}
{{ instructs.strats.inputs_intro }}
### Inputs
<{{ instructs.strats.strat_tag }}>
{{ instructs.strats.inputs }}
</{{ instructs.strats.strat_tag }}>

{%- endif%}

## Response Layout and Format
{% if instructs.io %}
### Response Layout:
The following is a {{ instructs.strats.fmt.upper() }} template to be used for the expected LLM response. For clarity, comments {{ instructs.strats.fmt_comment }} have been added between the lines.

<!-- <io_template> -->
{{ instructs.io }}
<!-- </io_template> -->

Merge all entries shown in '<io_template>' into a single {{ instructs.strats.fmt.upper() }} string. Your response should be shorter than {{ instructs.default_max_words }} words. Do NOT include comments {{ instructs.strats.fmt_comment }} or surrounding text!
{% elif instructs.strats.fmt %}
Answer using {{ instructs.strats.fmt.upper() }}! Do not include comments or surrounding text!
{% else %}
Answer in plain text! Do not include conversational text!
{% endif%}

## Your Task
{{ instructs.strats.method.data.your_task }}

Go strait to the answer!
Do not make any conversational comments!
Do not repeat any text provided in this prompt!
Do not explain your reasoning unless specifically asked for!