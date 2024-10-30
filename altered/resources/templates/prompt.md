{% extends "i_index.md" %}

{% block content %}

{% include "i_context.md" ignore missing %}

{% include "i_deliverable.md" ignore missing %}

<user_comment>
{% include "i_user_comment.md" ignore missing %}
</user_comment>


<INST>
{% include "i_instructs.md" ignore missing %}
</INST>

{% endblock %}