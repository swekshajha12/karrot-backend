from rest_framework.test import APITestCase

from config import settings
from foodsaving.groups.factories import GroupFactory
from foodsaving.invitations.models import Invitation
from foodsaving.userauth.models import VerificationCode
from foodsaving.users.factories import UserFactory
from foodsaving.utils import email_utils


class TestEmailUtils(APITestCase):
    def setUp(self):
        self.group = GroupFactory()
        self.user = UserFactory()

    def test_emailinvitation(self):
        invitation = Invitation.objects.create(
            email='bla@bla.com',
            group=self.group,
            invited_by=self.user
        )
        email = email_utils.prepare_emailinvitation_email(invitation)
        self.assertEqual(len(email.alternatives), 0)
        self.assertEqual(email.to[0], 'bla@bla.com')
        self.assertIn(self.group.name, email.body)
        self.assertIn(self.user.display_name, email.body)
        self.assertIn(str(invitation.token), email.body)
        self.assertIn(settings.SITE_NAME, email.body)
        self.assertIn(settings.HOSTNAME, email.body)
        self.assertNotIn('&amp;', email.body)

    def test_mailverification(self):
        verification_code = VerificationCode.objects.get(user=self.user)
        email = email_utils.prepare_mailverification_email(
            user=self.user,
            verification_code=verification_code,
        )
        self.assertEqual(email.to[0], self.user.unverified_email)

        self.assertEqual(len(email.alternatives), 1)
        html, mimetype = email.alternatives[0]

        self.assertEqual(mimetype, 'text/html')

        self.assertIn(self.user.display_name, email.body)
        self.assertIn(settings.SITE_NAME, email.body)
        self.assertIn(settings.HOSTNAME, email.body)
        self.assertIn(verification_code.code, email.body)

        self.assertIn(self.user.display_name, html)
        self.assertIn(settings.SITE_NAME, html)
        self.assertIn(settings.HOSTNAME, html)
        self.assertIn(verification_code.code, html)

    def test_send_new_verification_code(self):
        verification_code = VerificationCode.objects.get(user=self.user)
        email = email_utils.prepare_send_new_verification_code_email(self.user, verification_code)
        self.assertEqual(len(email.alternatives), 0)
        self.assertEqual(email.to[0], self.user.unverified_email)
        self.assertIn(settings.HOSTNAME, email.body)
        self.assertIn(verification_code.code, email.body)
