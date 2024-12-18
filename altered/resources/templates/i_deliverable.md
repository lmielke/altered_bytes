{%- if deliverable %}
<deliverable>

# 2. Deliverable: ({{ deliverable.name }} v_{{ deliverable.version|default("0.1") }})

Below you find the latest version __Deliverable__  or Object of Interest of this prompt.

```{{ deliverable.deliverable_fmt }}

{{ deliverable.content }}

```

{% if deliverable.selection %}
## Selection: 
{{ deliverable.selection }}
{% endif %}

</deliverable>
{% endif%}