
## General Background/History
### Original Prompt
This is the original prompt, which the entire chat is based on. Keep this in mind at all times!
__role: {{ context.init_prompt.role }}, content: {{ context.init_prompt.content }}__

### Chat History
The following is short summary of the ongoing discussion regarding this prompt.
{%- for entry in context.chat_history %}
{{ loop.index }}. {{ entry.role }}: {{ entry.content }}
{%- endfor %}
... pls find the continuation below the <context> tag, inside <user_comment> or <INST> tags.

