# Vault

## Namespaces

Namespaces are "mini vaults" where data, policies, mounts, etc are all managed separately. `namespace_create.yml` reads a config file that defines each namespaces and creates / configures them all. We allow for variable secret interpolation in all config files. This allows you to perform lookups for secrets, including but not limited to `hashi_vault`.

**Implemented and tested functionality:**

Auth Methods:

- Azure

Secret Engines:

- Azure
- Database
- KV

## Dependencies

1. `pip install ansible hvac ansible-modules-hashivault` (consider using `--user` or a virtualenv)

## Requirements

- set the vars_files to include your config file or set `namespace_config_file` to the path to your file
- set environment variables:
  - VAULT_ADDR
  - VAULT_TOKEN

_Note: you can set these at the play level in your playbook_

## Invoke

After configuring your yaml file (details below), to run the playbook simply execute:

```bash
ansible-playbook namespace_create.yml -e namespace_config_file=<path to your namespace yaml definition>
or
ansible-playbook namespace_create.yml # uses the config/namespace_config.yml example file included
```

## Config YAML


Example of 3 namespace definitions:

 - root
 - namespace_1 (effectively a child of root)
 - namespace_1/child_1
```

root:
    policies: default,ns_admin

namespace_1:
    policies: default, secret_rw
    engines:
        - mount_type: kv
          mount_name: secret
          options:
            version: 2
    auths:
        - auth_type: azure
          roles: azure_role
          auth_config: azure_config
        - auth_type: approle
          roles: template

namespace_1/child_1:
    policies: default, secret_rw
    engines:
        - mount_type: kv
          mount_name: secret
          options:
            version: 2
    auths:
        - auth_type: azure
          roles: azure_role
          auth_config: azure_config
        - auth_type: approle
          roles: template
```


### **auths**: (dict, optional) - enable and configure auth methods

#### auth shared variables

- auth_type: (string, req) - type of [auth method](https://www.vaultproject.io/docs/auth/)
- auth_name: (string, opt) - name of mount_point. defaults to `auth_type`
- mount_config: (dict, opt) - configuration of auth method mount. choices: `default_lease_ttl`, `max_lease_ttl`, `force_no_cache`, `token_type`

#### azure

- *all shared variables*
- auth_config: (file, opt) - further configuration of auth method. refers to a file name in `auths/<auth_type>/config/filename.json`. '/'s will be treated as a further directory
- roles: (string, opt) - refers to a filename in `auths/<auth_type>/roles/filename.json`

config example:
```
$ cat auths/azure/config/template.json
{
    "resource": "https://management.azure.com/",
    "tenant_id": "",
    "client_id": "",
    "client_secret": "{{ lookup('hashi_vault', 'secret=secret/data/az-auth-secret validate_certs=false')['data']['password'] }}"
}
```

role example:
```
$ cat auths/azure/roles/template.json
{
    "policies": ["test"],
    "bound_resource_groups": [""],
    "bound_subscription_ids": [""]
}
```

### **engines**: (dict, optional) enable a secret engine in the namespace. currently tested: kv, azure, database. some options must be set per engine type (see below)

#### engine shared variables

- mount_type: (string, req) - type of [secret engine](https://www.vaultproject.io/docs/secrets/)
- mount_name: (string, opt) - name of mount_point. defaults to `mount_type`
- mount_config: (dict, opt) - configuration of secret engine mount. choices: `default_lease_ttl`, `max_lease_ttl`, `force_no_cache`

#### kv

- *all shared variables*
- options: (dict, opt) - currently can only take 1 value `version` (string): choices `"1"` or `"2"`

#### azure

- *all shared variables*
- engine_config: (file, opt) - further configuration of secret engine. refers to a file name in `engines/<mount_type>/config/filename.json`. '/'s will be treated as a further directory
- roles: (string, opt) - refers to a filename in `engines/<mount_type>/roles/filename.json`

config example:
```
$ cat engines/azure/config/template.json
{
    "subscription_id": "",
    "client_id": "",
    "client_secret": "{{ lookup('hashi_vault', 'secret=secret/data/az-eng-secret validate_certs=false')['data']['password'] }}",
    "tenant_id": ""
}
```

role example:
```
$ cat engines/azure/roles/template.json
{
    "azure_role": "[{ 'role_name': 'Contributor','scope': '/subscriptions/'}]"
}
```

#### database

- *all shared variables*
- engine_config: (file, opt) - further configuration of secret engine. refers to a file name in `engines/<mount_type>/config/filename.json`. '/'s will be treated as a further directory
- roles: (string, opt) - refers to a filename in `engines/<mount_type>/roles/filename.json`

config example:
```
$ cat engines/database/config/template.json
{
    "plugin_name": "postgresql-database-plugin",
    "allowed_roles": [""],
    "username": "@",
    "password": "",
    "connection_url": "postgresql://{{'{{username}}'}}:{{'{{password}}'}}@database.com:5555"
}
```

role example:
```
$ cat engines/database/roles/template.json
{
    "creation_statements": [],
    "revocation_statements": [],
    "rollback_statements": [],
    "db_name": "" <-- needs to match the connection name you created. eg. `roles`
}

```

### **policies**: (string, optional)

- comma-separated list of all policies to write to this namespace. this looks for policies/policy.hcl files and will name the policy the file name minus *.hcl. default will always write (is required to be in policies/).

### **associations**: (list with nested dict, optional)

- define which policies will be associated with specific auth paths. example, the ldap group "group_1" is getting the "secret_rw" policy. policies can also be comman-separated


## Version 2.0 graveyard (work in progress)

these features from 1.0 likely will not work. working to fix this

### policy associations

### **ldap**: (bool, optional)

- true will look for files/ldap.json and enable and ldap auth method in namespace **this will be moved to `auths` one day**

#### pki

- mount_name (string, req)
- max_ttl: (string, opt, default('50m'))
- default_ttl: (string, opt, default('5m'))
- ca_int: (bool, opt) - setup pki as intermediate CA, not implemented yet