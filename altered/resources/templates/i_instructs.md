{%- if instructs %}
# 3. Instructions (INST)
{{ instructs.assi_role }}
{{ instructs.intro }}

{%- if instructs.strats %}
{%- include "i_instructs_strats.md" ignore missing %}
{%- endif %}

{%- endif %}

Do not make any conversational comments!
Do not repeat any text or tags provided in this prompt!
Do not explain your reasoning unless specifically asked for!