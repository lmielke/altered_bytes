{%- if instructs.io %}
Belows template example '{{ instructs.io.name }}' answers a hypothetical '{{ instructs.io.example }}' question. This '{{ instructs.io.fmt.upper() }}' template must be used to create the LLM response to your question.

```{{ instructs.io.fmt.lower() }}

{{ instructs.io.io_method.body }}
```

Respond with a '{{ instructs.io.fmt.upper() }}' string containing all entries shown in the Response Layout.
Your response should be shorter than {{ instructs.num_predict | default('250') }} words. Do NOT include comment lines starting with {{ instructs.io.fmt_comment }}!
{%- else %}
The requested response format is MARKDOWN text, like shown below:
instructs.io: {{ instructs.io }}
```markdown
# Answer
Your strait to the point answer goes here.
```
{% endif%}