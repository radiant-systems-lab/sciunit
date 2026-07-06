import base64
import json
import os
import re
import secrets
import shutil
import stat
from pathlib import Path

from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from sciunit2.exceptions import CommandError


SECURITY_DIRNAME = '.sciunit-security'
MANIFEST_NAME = 'manifest.json'
VAULT_NAME = 'secrets.enc'
KEY_CACHE_DIRNAME = '.sciunit-local'
KEY_CACHE_NAME = 'keys.json'

WHOLE_FILE_ARTIFACTS = (
    Path('cde.full-environment.cde-root'),
    Path('cde-root/home/root/.ipython/profile_default/history.sqlite'),
)

TEXT_SUFFIXES = {
    '.py', '.ipynb', '.json', '.yaml', '.yml',
    '.toml', '.ini', '.cfg', '.env', '.sh',
}

SECRET_NAMES = {
    'PASSWORD',
    'PASSWD',
    'PWD',
    'SECRET',
    'CLIENT_SECRET',
    'API_KEY',
    'API_SECRET',
    'SMTP_PASSWORD',
    'TOKEN',
    'ACCESS_TOKEN',
    'REFRESH_TOKEN',
    'SESSION_TOKEN',
    'JUPYTERHUB_API_TOKEN',
    'JPY_API_TOKEN',
    'SES_USER_TOKEN',
    'GITHUB_TOKEN',
    'AUTH_TOKEN',
    'BEARER_TOKEN',
    'ID_TOKEN',
    'JWT',
    'AUTHORIZATION',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'PRIVATE_KEY',
    'SSH_KEY',
}

PII_NAMES = {
    'EMAIL',
    'SMTP_EMAIL',
    'YOUR_EMAIL',
    'SENDER_EMAIL',
    'FROM_EMAIL',
}

ARGON2_SALT_BYTES = 16
ARGON2_MEMORY_KIB = 65536
ARGON2_TIME_COST = 3
ARGON2_PARALLELISM = 1
AES_KEY_BYTES = 32
AES_NONCE_BYTES = 12
KEY_NAME_PATTERN = r'[A-Za-z_][A-Za-z0-9_ -]{0,80}'
SECRET_NAME_PARTS = {
    'SECRET',
    'PASSWORD',
    'PASSWD',
    'PWD',
    'CREDENTIAL',
    'CREDENTIALS',
}
SECRET_NAME_SUFFIXES = (
    '_TOKEN',
    '_SECRET',
    '_PASSWORD',
    '_PASSWD',
    '_CREDENTIAL',
    '_CREDENTIALS',
)


def protect_execution(pkgdir, rev):
    pkg_path = Path(pkgdir)
    security_dir = pkg_path / SECURITY_DIRNAME
    shutil.rmtree(security_dir, ignore_errors=True)

    manifest = {'version': 1, 'files': [], 'artifacts': []}
    vault_items = []
    state = {'secret': 0, 'pii': 0, 'artifact': 0}

    artifact_entries = _protect_whole_artifacts(pkg_path, manifest, vault_items,
                                                state)
    file_entries = _protect_text_files(pkg_path, manifest, vault_items, state)

    if not artifact_entries and not file_entries:
        shutil.rmtree(security_dir, ignore_errors=True)
        return {'protected': False}

    security_dir.mkdir(parents=True, exist_ok=True)
    shared_key = _generate_shared_key()
    envelope = _encrypt_vault(vault_items, shared_key)

    _write_json(security_dir / MANIFEST_NAME, manifest)
    _write_json(security_dir / VAULT_NAME, envelope)

    return {
        'protected': True,
        'share_key': shared_key,
        'artifact_count': len(manifest['artifacts']),
        'file_count': len(manifest['files']),
    }


def restore_execution(pkgdir, shared_key):
    pkg_path = Path(pkgdir)
    manifest_path = pkg_path / SECURITY_DIRNAME / MANIFEST_NAME
    vault_path = pkg_path / SECURITY_DIRNAME / VAULT_NAME

    if not manifest_path.exists() or not vault_path.exists():
        return False

    manifest = _read_json(manifest_path)
    vault_items = _decrypt_vault(_read_json(vault_path), shared_key)
    items_by_id = {item['id']: item for item in vault_items}

    for artifact in manifest.get('artifacts', []):
        item = items_by_id[artifact['id']]
        target = pkg_path / artifact['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(item['value_b64']))

    for entry in manifest.get('files', []):
        target = pkg_path / entry['path']
        if not target.exists():
            continue
        content = target.read_text(encoding='utf-8')
        for replacement in entry['replacements']:
            item = items_by_id[replacement['id']]
            content = content.replace(replacement['placeholder'], item['value'])
        target.write_text(content, encoding='utf-8')

    return True


def package_requires_unlock(pkgdir):
    security_dir = Path(pkgdir) / SECURITY_DIRNAME
    return ((security_dir / MANIFEST_NAME).exists()
            and (security_dir / VAULT_NAME).exists())


def cache_shared_key(project_root, rev, shared_key):
    cache_path = _key_cache_path(project_root)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if cache_path.exists():
        data = _read_json(cache_path)
    data[rev] = shared_key
    _write_json(cache_path, data)
    os.chmod(cache_path, stat.S_IRUSR | stat.S_IWUSR)


def cached_shared_key(project_root, rev):
    cache_path = _key_cache_path(project_root)
    if not cache_path.exists():
        return None
    data = _read_json(cache_path)
    return data.get(rev)


def _key_cache_path(project_root):
    return Path(project_root) / KEY_CACHE_DIRNAME / KEY_CACHE_NAME


def _protect_whole_artifacts(pkg_path, manifest, vault_items, state):
    protected = []
    for rel_path in WHOLE_FILE_ARTIFACTS:
        target = pkg_path / rel_path
        if not target.exists():
            continue
        state['artifact'] += 1
        item_id = f'art_{state["artifact"]:03d}'
        vault_items.append({
            'id': item_id,
            'class': 'artifact',
            'path': rel_path.as_posix(),
            'value_b64': base64.b64encode(target.read_bytes()).decode('ascii'),
        })
        manifest['artifacts'].append({
            'id': item_id,
            'path': rel_path.as_posix(),
        })
        target.unlink()
        protected.append(rel_path.as_posix())
    return protected


def _protect_text_files(pkg_path, manifest, vault_items, state):
    protected = []
    search_root = pkg_path / 'cde-root' / 'home'
    if not search_root.exists():
        return protected

    for path in search_root.rglob('*'):
        if not path.is_file():
            continue
        if '__pycache__' in path.parts:
            continue
        if path.name == 'history.sqlite':
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != '.env':
            continue

        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b'\x00' in data:
            continue
        try:
            content = data.decode('utf-8')
        except UnicodeDecodeError:
            continue

        replacements, new_content = _redact_content(content, state, vault_items)
        if not replacements:
            continue

        rel_path = path.relative_to(pkg_path).as_posix()
        manifest['files'].append({
            'path': rel_path,
            'replacements': replacements,
        })
        path.write_text(new_content, encoding='utf-8')
        protected.append(rel_path)
    return protected


def _redact_content(content, state, vault_items):
    matches = []
    flags = re.IGNORECASE | re.MULTILINE
    patterns = [
        re.compile(
            rf'(?P<prefix>["\']?(?P<key>{KEY_NAME_PATTERN})["\']?'
            rf'[ \t]*[:=][ \t]*)'
            rf'(?P<quote>\\?["\'])(?P<value>.*?)(?P=quote)',
            flags),
        re.compile(
            rf'^(?P<prefix>\s*["\']?(?P<key>{KEY_NAME_PATTERN})["\']?'
            rf'[ \t]*[:=][ \t]*)'
            rf'(?P<value>[^\n#,"\'\}}\]]+?)\s*(?:[,\}}])?$',
            flags),
    ]

    for pattern in patterns:
        for match in pattern.finditer(content):
            name = _normalize_name(match.group('key'))
            class_ = _classify_name(name)
            if class_ is None:
                continue
            value = match.group('value').strip()
            if not value or value.startswith('__SCIUNIT_'):
                continue
            item_id = _next_id(class_, state)
            placeholder = _placeholder_for(class_, item_id)
            matches.append({
                'start': match.start('value'),
                'end': match.end('value'),
                'id': item_id,
                'class': class_,
                'placeholder': placeholder,
                'value': value,
            })

    if not matches:
        return [], content

    matches.sort(key=lambda item: (item['start'], item['end']))
    deduped = []
    last_end = -1
    for match in matches:
        if match['start'] < last_end:
            continue
        deduped.append(match)
        last_end = match['end']

    parts = []
    cursor = 0
    replacements = []
    for match in deduped:
        parts.append(content[cursor:match['start']])
        parts.append(match['placeholder'])
        cursor = match['end']
        replacements.append({
            'id': match['id'],
            'class': match['class'],
            'placeholder': match['placeholder'],
        })
        vault_items.append({
            'id': match['id'],
            'class': match['class'],
            'value': match['value'],
        })
    parts.append(content[cursor:])

    return replacements, ''.join(parts)


def _normalize_name(name):
    name = re.sub(r'(?i)^\s*export\s+', '', name)
    normalized = re.sub(r'[^A-Za-z0-9]+', '_', name.upper())
    normalized = re.sub(r'_+', '_', normalized).strip('_')
    return normalized


def _classify_name(name):
    if name in PII_NAMES:
        return 'pii'
    if name in SECRET_NAMES:
        return 'secret'

    parts = set(name.split('_'))
    if parts & SECRET_NAME_PARTS:
        return 'secret'
    if name.endswith(SECRET_NAME_SUFFIXES):
        return 'secret'
    if name.endswith('_KEY') and ('API' in parts or 'AWS' in parts):
        return 'secret'
    return None


def _next_id(class_, state):
    state[class_] += 1
    prefix = 'sec' if class_ == 'secret' else 'pii'
    return f'{prefix}_{state[class_]:03d}'


def _placeholder_for(class_, item_id):
    if class_ == 'secret':
        return f'__SCIUNIT_SECRET_{item_id}__'
    return f'__SCIUNIT_PII_{item_id}__'


def _generate_shared_key():
    return secrets.token_urlsafe(24)


def _encrypt_vault(vault_items, shared_key):
    vault_data = json.dumps({
        'version': 1,
        'items': vault_items,
    }, separators=(',', ':')).encode('utf-8')

    salt = secrets.token_bytes(ARGON2_SALT_BYTES)
    key = hash_secret_raw(shared_key.encode('utf-8'), salt, ARGON2_TIME_COST,
                          ARGON2_MEMORY_KIB, ARGON2_PARALLELISM,
                          AES_KEY_BYTES, Type.ID)
    nonce = secrets.token_bytes(AES_NONCE_BYTES)
    ciphertext = AESGCM(key).encrypt(nonce, vault_data, None)

    return {
        'version': 1,
        'kdf': {
            'name': 'argon2id',
            'salt_b64': base64.b64encode(salt).decode('ascii'),
            'memory_kib': ARGON2_MEMORY_KIB,
            'time_cost': ARGON2_TIME_COST,
            'parallelism': ARGON2_PARALLELISM,
        },
        'cipher': {
            'name': 'aes-256-gcm',
            'nonce_b64': base64.b64encode(nonce).decode('ascii'),
            'ciphertext_b64': base64.b64encode(ciphertext).decode('ascii'),
        },
    }


def _decrypt_vault(envelope, shared_key):
    try:
        salt = base64.b64decode(envelope['kdf']['salt_b64'])
        nonce = base64.b64decode(envelope['cipher']['nonce_b64'])
        ciphertext = base64.b64decode(envelope['cipher']['ciphertext_b64'])
        key = hash_secret_raw(
            shared_key.encode('utf-8'),
            salt,
            envelope['kdf']['time_cost'],
            envelope['kdf']['memory_kib'],
            envelope['kdf']['parallelism'],
            AES_KEY_BYTES,
            Type.ID,
        )
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode('utf-8'))['items']
    except Exception as exc:  # pragma: no cover - exact crypto errors vary
        raise CommandError('invalid unlock key') from exc


def _write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, sort_keys=True)


def _read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)
