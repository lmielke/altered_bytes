# Package Data
The following section shows package information to be used.

## Package Import Structure starting at {{ context.package_infos.root_file_name }}
```dot
{{ context.package_infos.digraph }}
```

## Installed Libraries
```{{ context.package_infos.req_format }}
{{ context.package_infos.requirements }}
```

## Package Structure
```text
{{ context.package_infos.tree }}
```

{% if context.package_infos.selected_files %}
## Selected Files
{% for file in context.package_infos.selected_files %}
### File {{ loop.index }}:  {{ file.file_path }}
```{{ file.file_type }}

{{ file.file_content }}

```
{% endfor %}
{% endif %}
