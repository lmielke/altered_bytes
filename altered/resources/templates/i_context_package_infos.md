## Package Info
The following section shows used Package information.

{%   if context.package_infos.digraph %}
### Package Import Structure starting at {{ context.package_infos.root_file_name }}
```dot
{{ context.package_infos.digraph }}
```
{%- endif %}

### Installed Package Libraries
```{{ context.package_infos.req_format }}
{{ context.package_infos.requirements }}
```

### Package File Structure
```text
{{ context.package_infos.tree }}
```

{% if context.package_infos.selected_files %}
### Top {{ context.package_infos.selected_files|length }} Selected Package Files
{% for file in context.package_infos.selected_files %}
#### File {{ loop.index }}:  {{ file.file_path }}
```{{ file.file_type }}

{{ file.file_content }}

```
{% endfor %}
{% endif %}
