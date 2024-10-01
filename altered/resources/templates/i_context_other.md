
## Additional Context

{%- for key, value in context.items() %}
  {%- if key not in ['history', 'rag_selection'] and value is not none %}
### {{ key|capitalize }}
{{ value }}
  {%- endif %}
{%- endfor %}