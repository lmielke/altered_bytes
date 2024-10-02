{%- if instructs.io %}
### Response Layout:
The following {{ instructs.strats.fmt.upper() }} template answers a simple 'Hi, who are you?' example question. This template must be used to create the LLM response to your question.

```{{ instructs.strats.fmt.lower() }}

{{ instructs.io }}

```

Respond with a {{ instructs.strats.fmt.upper() }} string containing all entries shown 
in Response Layout. Your response should be shorter than {{ instructs.default_max_words }} words. Do NOT include comment lines starting with {{ instructs.strats.fmt_comment }}!

{%- elif instructs.strats.fmt %}
The requested response format is {{ instructs.strats.fmt.upper() }}!
{%- else %}
Answer in MARKDOWN text like:
```markdown
# Answer
Your strait to the point answer here without comments or conversational text.
```
{% endif%}