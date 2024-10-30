## Search Content (Google Search)
The following {{ context.search_results|length }} results have been parsed from Goole Search. Since the Google Search results have not yet been veryfied, they might or might not be relevant to the current prompt.

### Search Query
"{{ context.search_query }}"
{% if context.search_results %}
#### Search Results
{% for entry in context.search_results %}
{%- if entry.agg %}
The search results have been aggregated to a single result using {{ entry.agg }}.
{%- endif %}
{{ loop.index }}. " _{{ entry.source }}_ "
{{ entry.content }}
{% endfor %}
{% else %}
No search results provided.
{% endif %}


