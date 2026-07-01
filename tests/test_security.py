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

    def test_key_cache(self):
        project_root = os.path.join('tmp', 'proj')
        sciunit2.security.cache_shared_key(project_root, 'e7', 'shared-key')
        self.assertEqual('shared-key',
                         sciunit2.security.cached_shared_key(project_root,
                                                             'e7'))
