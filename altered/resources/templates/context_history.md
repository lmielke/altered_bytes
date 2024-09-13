
## Chat History
This is what was discussed so far.
{%- for entry in context.chat_history %}
{{ loop.index }}. {{ entry.role }}: {{ entry.content }}
{%- endfor %}
The recent chat question will be provided as <user_prompt> further below in this prompt.

