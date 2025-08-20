The requested response format is {{ instructs.fmt | upper }}, like shown below:
{%- if instructs.fmt == 'markdown' %}
```markdown
# Answer
Your strait to the point answer goes here.
```
<optional_comment> In very rare cases, additional comments might be necessary. </optional_comment>

{% elif instructs.fmt == 'text' %}
Answer:
Your strait to the point answer goes here.

Optional Comment:
In very rare cases, additional comments might be necessary.

{% elif instructs.fmt == 'html' %}
```html
<div class="answer">
  <h2>Answer</h2>
  <p>Your straight to the point answer goes here.</p>
  <optional_comment>
    In very rare cases, additional comments might be necessary.
  </optional_comment>
</div>
```
{%- endif %}