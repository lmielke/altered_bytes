## Users Operating System Information
The following must be taken into consideration when providing technical and coding support.
For example, provided shell commands must consider the Shell/Ui used by the User.
### Operating System
**OS**: {{ context.sys_info.os }}

### Network
**Hostname**: {{ context.sys_info.hostname }}
**IP Address**: {{ context.sys_info.ip_address }}

### User
**Username**: {{ context.sys_info.username }}

### PowerShell Version Information
**PS Version**: {{ context.sys_info.psversiontable.PSVersion }}
**PS Edition**: {{ context.sys_info.psversiontable.PSEdition }}

### Disks
{% for disk_key, disk in context.sys_info.disk_info.items() %}
**Disk**: {{ disk_key }}
  - **Capacity**: {{ disk.TotalSizeGB }} GB
  - **Free Space**: {{ disk.FreeSpaceGB }} GB
{% endfor %}
