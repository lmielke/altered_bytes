### Response Layout:
The following '{{ instructs.io.fmt.upper() }}' template answers a simple 'Hi, who are you?' example question. This template must be used to create the LLM response to your question.

```{{ instructs.io.fmt.lower() }}

{{ instructs.io.method.body }}
```

Respond with a '{{ instructs.io.fmt.upper() }}' string containing all entries shown in the Response Layout.
Your response should be shorter than {{ instructs.response_max_words | default('250') }} words. Do NOT include comment lines starting with {{ instructs.io.fmt_comment }}!

{%- if instructs.io.fmt %}
The requested response format is '{{ instructs.io.fmt.upper() }}'!
{%- else %}
Answer in MARKDOWN text like:
```markdown
# Answer
Your strait to the point answer here without comments or conversational text.
```
{% endif%}