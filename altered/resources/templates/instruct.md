{%- if instruct %}
You are a helpful assistant!
{%- for key, value in instruct.items() %}
{%- if key not in ['assi_role'] and value is not none %}
# {{ key|capitalize }}
{{ value }}
{%- endif %}
{%- endfor %}
{%- endif %}