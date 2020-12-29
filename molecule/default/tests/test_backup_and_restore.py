import json

import os

import re

import sys

import testinfra.utils.ansible_runner

import uuid

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def update_service(host, service_name, state):
    if host.system_info.distribution == 'debian':
        return host.run("/etc/init.d/%s %s",
                        service_name, state)

    return host.run("systemctl %s %s", state, service_name)

def test_backup_files(host):
    pgbackrest_conf_path = "/etc/pgbackrest/pgbackrest.conf"
    postgresql_data_path = "/var/lib/pgsql/data"
    test_uuid = uuid.uuid4()

    if host.system_info.distribution == 'debian':
        if re.match(r'^9', host.system_info.release):
            postgresql_data_path = "/var/lib/postgresql/9.6/main"
        elif re.match(r'^10', host.system_info.release):
            postgresql_data_path = "/var/lib/postgresql/11/main"

    # Check the pgbackrest status
    with host.sudo("postgres"):
        status = host.run(
            (
                "pgbackrest "
                "--config=%s "
                "--stanza=main "
                "--log-level-console=info "
                "check"
            ),
            pgbackrest_conf_path
        )
        assert status.exit_status == 0

    # Add a database and database entry
    with host.sudo("postgres"):
        host.run("createdb test")
        host.run("psql -c \"CREATE TABLE testtable (id int, name varchar)\" test")
        host.run(
            (
                "psql -c \"INSERT INTO testtable (id, name) "
                "VALUES (999, '%s')\" test"
            ),
            str(test_uuid),
        )
        result = host.run("psql -c \"SELECT * FROM testtable LIMIT 1\" -t test")
        assert result.exit_status == 0

    # Attempt a backup with pgbackrest
    with host.sudo("postgres"):
        backup = host.run(
            "/usr/local/bin/pgbackrest_backup -c %s full",
            pgbackrest_conf_path
        )

        print(backup)
        assert backup.exit_status == 0

    # Ruin the database and restore
    rmcmd = host.run("rm -f -- %s/global/pg_control", postgresql_data_path)

    restart = update_service(host, "postgresql", "restart")
    assert restart.exit_status != 0

    restore = host.run("/usr/local/bin/pgbackrest_restore main")
    assert restore.exit_status == 0

    statuscmd = update_service(host, "postgresql", "start")
    assert statuscmd.exit_status == 0
