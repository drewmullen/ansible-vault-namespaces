import os
import requests

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

token = os.environ['VAULT_TOKEN']
headers = {'X-Vault-Token': token}
url = os.environ['VAULT_ADDR']
default_ttl = 2764800
verify = False

def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'

def test_api_available(host):
    r = requests.get(url + '/v1/sys/health', verify=verify).json()
    assert r['sealed'] == False

def test_kv_default(host):
    r = requests.get(url + '/v1/parent_ns/sys/mounts/kv/tune', verify=verify, headers=headers)
    assert r.status_code == 200
    assert "version" not in r.json()['data']
    assert r.json()['data']['default_lease_ttl'] == default_ttl
    assert r.json()['data']['max_lease_ttl'] == default_ttl

def test_kv2(host):
    r = requests.get(url + '/v1/parent_ns/sys/mounts/kv2/tune', verify=verify, headers=headers)
    assert r.status_code == 200
    assert r.json()['data']['options']['version'] == "2"
    assert r.json()['data']['default_lease_ttl'] == default_ttl
    assert r.json()['data']['max_lease_ttl'] == default_ttl

def test_kv_configured(host):
    r = requests.get(url + '/v1/parent_ns/sys/mounts/kv3/tune', verify=verify, headers=headers)
    assert r.status_code == 200
    assert r.json()['data']['default_lease_ttl'] == 500
    assert r.json()['data']['max_lease_ttl'] == 550

def test_write_secret(host):
    secret_json = {'name': 'drew'}
    r = requests.post(
        url + '/v1/parent_ns/kv/test_secret',
        verify=verify,
        headers=headers,
        json=secret_json
        )

    assert r.status_code == 204

def test_approle_exists(host):
    r = requests.get(
        url + '/v1/parent_ns/auth/approle/role/testrole',
        verify=verify,
        headers=headers
        )

    assert r.status_code == 200

def test_approle_login(host):
    role_id = requests.get(
        url + '/v1/parent_ns/auth/approle/role/testrole/role-id',
        verify=False,
        headers=headers
        ).json()['data']['role_id']
    secret_id = requests.post(
        url + '/v1/parent_ns/auth/approle/role/testrole/secret-id',
        verify=False,
        headers=headers
        ).json()['data']['secret_id']

    login_attempt = requests.post(
        url + '/v1/parent_ns/auth/approle/login',
        verify=False,
        headers=headers,
        json={
            'role_id': role_id,
            'secret_id': secret_id
            }
        )

        assert login_attempt.status_code == 200

    read_attempt = requests.get(
        url + '/v1/parent_ns/kv/test_secret',
        verify=False,
        headers={
            'X-Vault-Token': login_attempt.json()['auth']['client_token']
            }
        )
        assert read_attempt.status_code == 200
        assert read_attempt.json()['data']['name'] == "drew"
