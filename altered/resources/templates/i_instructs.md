{%- if instructs %}
# 3. Instructions (INST)
{{ instructs.assi_role }}
{{ instructs.intro }}

{%- if instructs.strats %}
{%- include "i_instructs_strats.md" ignore missing %}
{%- endif %}

{%- endif %}