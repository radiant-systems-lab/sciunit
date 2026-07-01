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

### CLI

- `sciunit2/cli.py`
- new command file: `sciunit2/command/unlock.py`

## What is intentionally not handled yet

- runtime session secrets such as `ACCESS_TOKEN`, `REFRESH_TOKEN`, and JupyterHub tokens
- env overlay / fresh session secret injection during repeat
- direct modification of `vvpkg.bin`

Those are planned as a later phase.
