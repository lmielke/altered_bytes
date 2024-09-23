{%- if instructs %}
{{ instructs.assi_role }}
{{ instructs.intro }}

{%- if instructs.strats %}
{%- include "instructs_strats.md" ignore missing %}
{%- endif %}

{%- endif %}