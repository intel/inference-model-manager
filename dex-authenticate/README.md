
# Dex authentication script - LDAP version

Simple script providing a way to authenticate against dex configured with LDAP as identity provider. As a result user receives JWT id_token containing information about groups he/she belongs to. Token is signed by dex private key and can be used to authorize its holder while requesting secured endpoints (like those in Mgmt API).

## How to use it?

 1. Create virtualenv with python3.
 2. Install dependencies from requirements.txt.
 3. Download and build dex as described in [getting started guide](https://github.com/coreos/dex/blob/master/Documentation/getting-started.md#building-the-dex-binary).
 4. Install openldap server.
 5. Run following script from dex repository:
```
    ./scripts/slapd.sh
```
In case of permission problems with slapd.sh script please ensure apparmor config has proper entries. For me additional lines were needed in /etc/apparmor.d/usr.sbin.slapd file: 
```
    /tmp/** rw,
    /local/path/to/dex/** rw,
```
 6. Edit ./examples/config-ldap.yaml in order to enable https on 0.0.0.0:5554 address (similar section is [here)](https://github.com/coreos/dex/blob/master/examples/config-dev.yaml#L18)
 7. Start dex with LDAP configuration.
```
    ./bin/dex serve examples/config-ldap.yaml
```
 8. Run actual script with authentication:
```
    python authenticate.py
```

## Notes
 1. For now, script authenticates janedoe@example.com user which is artificially populated in LDAP database.
 2. I were not able to identify completely API based (non-web) flow so there is HTML scrapping done in the process of token retrieval.
 3. All https requests to dex are not verified, although https enablement was necessary. It was enforced by oauth-requests library.
