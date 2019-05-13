# Vault

## Namespaces

Namespaces are "mini vaults" where data, policies, mounts, etc are all managed seperately. `namespace_create.yml` reads a config file that defines each namespaces and creates / configures them all.

## Requirements

- config/namespaces.yml
- download vault client locally to {{ vault_bin } (/usr/bin by default)

## Config YAML


Example:
```
namespace_1:
    ldap: true
    policies: default, secret_rw
    associations:
        - path: auth/ldap/groups/group_1
          policies: secret_rw
    engines:
        - mount_type: kv
          mount_name: secret
          version: 2
        - mount_type: azure
          mount_name: azure
    auths:
        - auth_type: azure
          role: azure_role
          config: azure_config
        - auth_type: approle
          role: template
```

Options:

### **auths**: (bool, optional)

- enable a auth mount

_approles_

- create approles from defined files in approles/*.json. note, you can associate policies via the `associations` option above.
- auth_type: (string, req)
- role: (string, req)

_azure_

- auth_type: (string, req)
- role: (string, req) - refers to a filename in `auths/<auth_type>/filename`
- config: (string, req) - refers to a filename in `auths/<auth_type>/filename`

### **ldap**: (bool, optional)

- true will look for files/ldap.json and enable and ldap auth method in namespace **this will be moved to `auths` one day**

### **policies**: (string, optional)

- comma-separated list of all policies to write to this namespace. this looks for policies/policy.hcl files and will name the policy the file name minus *.hcl. default will always write (is required to be in policies/).

### **associations**: (list with nested dict, optional)

- define which policies will be associated with specific auth paths. in the example, the ldap group "group_1" is getting the "secret_rw" policy. policies can also be comman-separated

### **engines**: (list with nested dict, optional)

- enable a secret engine in the namespace. currently tested: kv, azure, and pki. some options must be set per engine type (see below).

_kv_

- mount_name (string, req)
- version (string, opt, default(1))
- max_ttl: (string, opt, default('50m'))
- default_ttl: (string, opt, default('5m'))

_azure_

- mount_name (string, req)
- max_ttl: (string, opt, default('50m'))
- default_ttl: (string, opt, default('5m'))

_pki_

- mount_name (string, req)
- max_ttl: (string, opt, default('50m'))
- default_ttl: (string, opt, default('5m'))
- ca_int: (bool, opt) - setup pki as intermediate CA, not implemented yet

## Default Variables

vault_url: "{{ lookup('env','VAULT_ADDR') }}"

vault_bin: /usr/bin

namespace_config_file: namespace_config.yml
