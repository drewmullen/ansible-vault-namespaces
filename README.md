# Vault

## Namespaces

Namespaces are "mini vaults" where data, policies, mounts, etc are all managed seperately. `namespace_create.yml` reads a config file that defines each namespaces and creates / configures them all.

## Requirements

- config/namespaces.yml
- files/ldap.json
- download vault client locally to {{ vault_bin } (/usr/bin by default)

## Config YAML

```
namespace_1:
    ldap: true
    policies: default,secret_rw
    associations:
        - path: auth/ldap/groups/group_1
          policies: secret_rw
    engines:
        - mount_type: kv
          mount_name: secret
          version: 2
    approles:
      - role: my_app
        #max_ttl: 50m
```

Options:

### **ldap**: (bool, optional)

- true will look for files/ldap.json and enable and ldap auth method in namespace

### **policies**: (string, optional)

- comma-separated list of all policies to write to this namespace. no spaces after commas, please. this looks for policies/policy.hcl files and will name the policy the file name minus *.hcl. default will always write (is required to be in policies/).

### **associations**: (list with nested dict, optional)

- define which policies will be associated with specific auth paths. in the example, the ldap group "group_1" is getting the "secret_rw" policy. policies can also be comman-separated

### **engines**: (list with nested dict, optional)

- enable a secret engine in the namespace. currently working: kv and pki. some options must be set per engine type (see below).

_kv_

- mount_name (string, req)
- version (string, opt, default(1))
- max_ttl: (string, opt, default('50m'))
- default_ttl: (string, opt, default('5m'))

_pki_

- mount_name (string, req)
- version (string, opt, default(1))
- max_ttl: (string, opt, default('50m'))
- default_ttl: (string, opt, default('5m'))
- ca_int: (bool, opt) - setup pki as intermediate CA, not working yet

### **approles**: (list with nested dict, optional)

- create approles from defined files in approles/*.json. note, you can associate policies via the `associations` option above.

## Default Variables

vault_url: "{{ lookup('env','VAULT_ADDR') }}"

vault_bin: /usr/bin

namespace_config_file: namespace_config.yml

## Notes

You must specifically create each namespace if you want it to have children. example, you want child namespace group_a/team_b. you must specifically create a namespace entries in your namespace_config.yml file to create both `group_a` **AND** `group_a/team_b`.
