# Sciunit Secret Protection Changes

This document summarizes the code changes made for portable secret and sensitive PII protection.

## New behavior

Sciunit now protects generated `cde-package` contents before committing them to deduplicated storage.

### Protected artifacts

Whole-file protection:

- `cde.full-environment.cde-root`
- `cde-root/home/root/.ipython/profile_default/history.sqlite`

These files are removed from the plaintext package and stored only inside the encrypted vault.

### Redacted text files

Sciunit scans text files under `cde-root/home/...` with these suffixes:

- `.py`
- `.ipynb`
- `.json`
- `.yaml`
- `.yml`
- `.toml`
- `.ini`
- `.cfg`
- `.env`
- `.sh`

Supported v1 redaction classes:

- `secret`
- `pii`

Examples:

- `SMTP_PASSWORD` -> redacted as a secret
- `SMTP_EMAIL` -> redacted as PII
- `SMTP_SERVER` -> left plaintext as config

Additional token protection now includes common runtime and service token fields such as:

- `ACCESS_TOKEN`
- `REFRESH_TOKEN`
- `SESSION_TOKEN`
- `JUPYTERHUB_API_TOKEN`
- `JPY_API_TOKEN`
- `SES_USER_TOKEN`
- `GITHUB_TOKEN`
- `AUTHORIZATION`
- AWS access key fields
- private / SSH key fields

Jupyter kernel connection files under `.local/share/jupyter/runtime/kernel-*.json`
are handled as a scoped special case: their `key` field is redacted as a
runtime secret, while generic JSON fields named `key` outside that runtime path
are left alone unless another secret-name rule matches.

Generic key names ending in `_TOKEN`, `_SECRET`, `_PASSWORD`, `_PASSWD`, `_CREDENTIAL`,
or `_CREDENTIALS` are also treated as secrets. API/AWS-style `_KEY` names are
protected when the key name indicates API or AWS credentials. Derived metadata fields
such as `token_fingerprint` remain plaintext.

Supported assignment formats include quoted values, unquoted `.env` / shell values,
`export KEY=value` shell syntax, YAML `key: value` syntax, nested YAML blocks, and
escaped notebook JSON source strings.

## New storage layout in `cde-package`

When protection is needed, Sciunit adds:

- `.sciunit-security/manifest.json`
- `.sciunit-security/secrets.enc`

The manifest records which files were modified and which placeholders map to which encrypted items.
The encrypted vault stores both whole-file artifacts and value-level secret / PII entries.

## Encryption design

- KDF: `Argon2id`
- Cipher: `AES-256-GCM`
- One generated shared key per execution

The shared key is shown to the audit user after a protected commit.
The same key is cached locally for the audit user and can be shared out of band with a repeat user.

## New CLI command

```bash
sciunit unlock <execution id> --key <shared-key>
```

This caches the shared key locally so `sciunit repeat` and the repeat kernel can restore protected files after checkout.

## Changed code paths

### New module

- `sciunit2/security.py`

Responsibilities:

- whole-file protection for sensitive artifacts
- text-file redaction for portable secrets and PII
- manifest + encrypted vault creation
- restore after checkout
- local key cache management

### Commit path

- `sciunit2/command/mixin.py`

Before `repo.checkin(...)`, Sciunit now:

1. protects the package
2. commits only the protected form
3. caches the shared key locally after successful commit
4. prints the shared key in the commit note

### Repeat path

- `sciunit2/command/repeat.py`
- `sciunit2/command/given.py`

After checkout and before execution, Sciunit now:

1. detects whether the package is protected
2. loads the cached shared key
3. restores whole-file artifacts and placeholder values
4. runs repeat

If the package is protected and no key has been cached, repeat fails with an unlock instruction.

For notebook replay, the FLINC repeat handler surfaces this condition before the
notebook repeats. The user-facing message says the selected execution is encrypted,
prints `sciunit unlock <execution id> --key <shared-key>`, and tells the user to
restart the Sciunit Repeat Kernel after unlocking. Full Sciunit stdout/stderr is
kept in `flinc.log`.

Repeat scenarios:

- Protected package and no cached key: stop before execution and show the unlock
  command.
- Protected package and wrong cached key: stop with the decrypt / unlock failure.
- Protected package and correct cached key: restore encrypted artifacts and
  redacted values, then repeat normally.
- Unprotected package: repeat normally without an unlock prompt.

### CLI

- `sciunit2/cli.py`
- new command file: `sciunit2/command/unlock.py`

## What is intentionally not handled yet

- fresh runtime/session secret injection during repeat
- policy decisions about whether old session tokens should be restored, rotated, or
  replaced by environment overlays on the repeat side
- direct modification of `vvpkg.bin`

Runtime token values are now redacted from captured plaintext files when they appear
in supported assignment formats, but repeat-time rebinding remains a separate policy
phase.
