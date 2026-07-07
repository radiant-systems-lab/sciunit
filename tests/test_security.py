import os

from tests import testit
import sciunit2.security


class TestSecurity(testit.LocalCase):
    def test_protect_and_restore(self):
        pkgdir = os.path.join('tmp', 'proj', 'cde-package')
        testit.mkdir(os.path.join(pkgdir, 'cde-root/home/jovyan/work/demo'))
        testit.mkdir(os.path.join(pkgdir,
                                  'cde-root/home/root/.ipython/profile_default'))

        with open(os.path.join(pkgdir, 'cde.full-environment.cde-root'), 'w') as f:
            f.write('ACCESS_TOKEN=abc\nSAGE_API_URL=https://example.test\n')

        with open(os.path.join(pkgdir,
                               'cde-root/home/root/.ipython/profile_default/history.sqlite'), 'w') as f:
            f.write('SMTP_PASSWORD = "secret"\n')

        target = os.path.join(pkgdir, 'cde-root/home/jovyan/work/demo/app.py')
        with open(target, 'w') as f:
            f.write('SMTP_SERVER = "smtp.gmail.com"\n'
                    'SMTP_EMAIL = "person@example.com"\n'
                    'SMTP_PASSWORD = "very-secret"\n')

        protection = sciunit2.security.protect_execution(pkgdir, 'e1')
        self.assertTrue(protection['protected'])
        self.assertTrue(protection['share_key'])

        with open(target) as f:
            redacted = f.read()
        self.assertIn('__SCIUNIT_SECRET_sec_001__', redacted)
        self.assertIn('__SCIUNIT_PII_pii_001__', redacted)
        self.assertIn('smtp.gmail.com', redacted)
        self.assertNotIn('very-secret', redacted)
        self.assertNotIn('person@example.com', redacted)

        self.assertFalse(os.path.exists(os.path.join(
            pkgdir, 'cde-root/home/root/.ipython/profile_default/history.sqlite')))
        self.assertFalse(os.path.exists(os.path.join(
            pkgdir, 'cde.full-environment.cde-root')))

        self.assertTrue(sciunit2.security.package_requires_unlock(pkgdir))
        self.assertTrue(sciunit2.security.restore_execution(
            pkgdir, protection['share_key']))

        with open(target) as f:
            restored = f.read()
        self.assertIn('SMTP_PASSWORD = "very-secret"', restored)
        self.assertIn('SMTP_EMAIL = "person@example.com"', restored)

        with open(os.path.join(
                pkgdir,
                'cde-root/home/root/.ipython/profile_default/history.sqlite')) as f:
            self.assertIn('SMTP_PASSWORD = "secret"', f.read())

        with open(os.path.join(pkgdir, 'cde.full-environment.cde-root')) as f:
            self.assertIn('ACCESS_TOKEN=abc', f.read())

    def test_token_redaction_formats(self):
        state = {'secret': 0, 'pii': 0, 'artifact': 0}
        vault_items = []
        content = (
            'ACCESS_TOKEN = "runtime-token"\n'
            'refresh_token: fake-refresh-token\n'
            'Authorization: "Bearer live-token"\n'
            '\"GITHUB_TOKEN\": \"ghp_fakeToken\"\n'
            'auth:\n'
            '  API_KEY: sk-test-openmeteo-proxy\n'
            'token_fingerprint = "not-protected"\n'
            'SMTP_EMAIL = "person@example.com"\n'
        )

        replacements, redacted = sciunit2.security._redact_content(
            content, state, vault_items)

        self.assertEqual(6, len(replacements))
        self.assertNotIn('runtime-token', redacted)
        self.assertNotIn('fake-refresh-token', redacted)
        self.assertNotIn('Bearer live-token', redacted)
        self.assertNotIn('ghp_fakeToken', redacted)
        self.assertNotIn('sk-test-openmeteo-proxy', redacted)
        self.assertNotIn('person@example.com', redacted)
        self.assertIn('not-protected', redacted)
        self.assertEqual(5, len([item for item in vault_items
                                 if item['class'] == 'secret']))
        self.assertEqual(1, len([item for item in vault_items
                                 if item['class'] == 'pii']))

    def test_jupyter_connection_key_redaction(self):
        pkgdir = os.path.join('tmp', 'proj', 'cde-package')
        runtime = os.path.join(
            pkgdir,
            'cde-root/home/root/.local/share/jupyter/runtime')
        testit.mkdir(runtime)

        target = os.path.join(runtime, 'kernel-test.json')
        with open(target, 'w') as f:
            f.write('{\n'
                    '  "shell_port": 37147,\n'
                    '  "key": "live-jupyter-key",\n'
                    '  "signature_scheme": "hmac-sha256"\n'
                    '}\n')

        protection = sciunit2.security.protect_execution(pkgdir, 'e1')
        self.assertTrue(protection['protected'])

        with open(target) as f:
            redacted = f.read()
        self.assertIn('__SCIUNIT_SECRET_sec_001__', redacted)
        self.assertNotIn('live-jupyter-key', redacted)

        self.assertTrue(sciunit2.security.restore_execution(
            pkgdir, protection['share_key']))
        with open(target) as f:
            restored = f.read()
        self.assertIn('"key": "live-jupyter-key"', restored)

    def test_generic_json_key_is_not_redacted(self):
        state = {'secret': 0, 'pii': 0, 'artifact': 0}
        vault_items = []
        content = '{"key": "not-a-secret", "API_KEY": "secret"}'

        replacements, redacted = sciunit2.security._redact_content(
            content, state, vault_items,
            'cde-root/home/jovyan/work/config.json')

        self.assertEqual(1, len(replacements))
        self.assertIn('not-a-secret', redacted)
        self.assertNotIn('"secret"', redacted)

    def test_key_cache(self):
        project_root = os.path.join('tmp', 'proj')
        sciunit2.security.cache_shared_key(project_root, 'e7', 'shared-key')
        self.assertEqual('shared-key',
                         sciunit2.security.cached_shared_key(project_root,
                                                             'e7'))
