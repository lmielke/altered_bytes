{%- if instructs %}
# 3. Instructions (INST)
You where provided with text inside the {{ instructs.inputs }} tag.
The following instructions will outline, what to do with {{ instructs.inputs }}. Your response will be evaluated based on how well you follow the instructions.
{{ instructs.assi_role }}
{{ instructs.intro }}

{%- if instructs.strats %}
{%- include "i_instructs_strats.md" ignore missing %}
{%- endif %}

{%- endif %}

Do not make any conversational comments!
Do not repeat any text or tags provided in this prompt!
Do not explain your reasoning unless explicitly asked for!