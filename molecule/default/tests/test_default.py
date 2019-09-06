import os
import requests

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'

def test_api_available(host):
    r = requests.get(os.environ['VAULT_ADDR'] + '/v1/sys/health', verify=False).json()
    assert r['sealed'] == False
