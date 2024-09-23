## Search Content (Google Search)
The following {{ context.context_search_results|length }} results have been parsed from Goole Search. Since the Google Search results have not yet been veryfied, they might or might not be relevant to the current prompt.

### Search Query
" {{ context.context_search_query }} "

#### Search Results
{% for entry in context.context_search_results %}
{{ loop.index }}. " _{{ entry.source }}_ "
{{ entry.content }}
{% endfor %}

