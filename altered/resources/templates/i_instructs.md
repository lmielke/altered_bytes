{%- if instructs %}
# 3. Instructions (INST)
The following outlines the main instructions about, what to do with the content of this prompt. The model response will be evaluated based on how well it follows these instructions.
{{ instructs.assi_role }}
{{ instructs.intro }}

{%- if instructs.strats %}
{%- include "i_instructs_strats.md" ignore missing %}
{%- endif %}

{%- endif %}

Do not make any conversational comments!
Do not repeat any text or tags provided in this prompt!
Do not explain your reasoning unless explicitly asked for!