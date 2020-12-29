pgbackrest
=========

This role installs and configures pgBackRest (https://pgbackrest.org/).

Requirements
------------

Obviously this role depends on an installed and configured PostgreSQL cluster
to run backups from. It is expected that PostgreSQL has already been configured
and running by the time this role is used.

Role Variables
--------------

Please check [defaults/main.yml](defaults/main.yml) for the latest configurable
values for this role. Each variable should have an explanatory comment.

Dependencies
------------

None.

Example Playbook
----------------

    - hosts: pg_servers
      roles:
         - role: dudefellah.pgbackrest
           pgbackrest_conf_cluster_stanzas:
             main:
               pg_path: /var/lib/pgsql/data

License
-------

GPL-2.0+

Author Information
------------------

Dan - github.com/dudefellah
