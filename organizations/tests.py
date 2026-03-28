from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from files.tests import FileTestingHelper
from organizations.models import Organization

User = get_user_model()


# Endpoint for listing all organizations
class TestOrganizationList(TestCase):
    def setUp(self):
        # prepare the api
        self.client = APIClient()
        self.organizations_url = '/organizations/'

    def test_anonymous_user(self):
        # create organization
        organization_a = Organization.objects.create(name='organization_a')
        response = self.client.get(self.organizations_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_one_organization(self):
        # create organization
        organization_a = Organization.objects.create(name='organization_a')

        # create and log in a user
        self.user = User.objects.create_user(username='user', password='password123', organization=organization_a)
        self.client.login(username=self.user.username, password='password123')

        # check the organizations endpoint
        response = self.client.get(self.organizations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # map organizations to an array of names
        names = [org['name'] for org in response.data]

        self.assertIn(organization_a.name, names)

    def test_multiple_organizations(self):
        # create organizations
        organization_a = Organization.objects.create(name='organization_a')
        organization_b = Organization.objects.create(name='organization_b')

        # create and log in a user
        self.user = User.objects.create_user(username='user', password='password123', organization=organization_a)
        self.client.login(username=self.user.username, password='password123')

        # check the organizations endpoint
        response = self.client.get(self.organizations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # map organizations to an array of names
        names = [org['name'] for org in response.data]

        self.assertIn(organization_a.name, names)
        self.assertIn(organization_b.name, names)


# ... including the total download count per organization
class TestOrganizationDownloads(TestCase):
    def setUp(self):
        # populate the organizations
        self.organization_a = Organization.objects.create(name='organization_a')
        self.organization_b = Organization.objects.create(name='organization_b')

        # populate users
        self.uploading_user = User.objects.create_user(
            username='uploading_user',
            password='password123',
            organization=self.organization_a,
        )
        self.user_in_same_org = User.objects.create_user(
            username='user_in_same_org',
            password='password123',
            organization=self.organization_a,
        )
        self.user_in_external_org = User.objects.create_user(
            username='user_in_external_org',
            password='password123',
            organization=self.organization_b,
        )

        # prepare the api
        self.client = APIClient()
        self.files_url = '/files/'
        self.organizations_url = '/organizations/'
        self.uploaded_file_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.uploading_user.username,
            password='password123',
        )
        self.download_url = f'/download/{self.uploaded_file_id}'

    def test_no_downloads(self):
        self.client.login(username=self.uploading_user.username, password='password123')
        self._test_download_count(0)

    def test_multiple_downloads_from_one_user(self):
        self.client.login(username=self.user_in_same_org.username, password='password123')
        self.client.get(self.download_url)
        self.client.get(self.download_url)
        self._test_download_count(2)

    def test_different_organisations_downloading(self):
        self.client.login(username=self.user_in_external_org.username, password='password123')
        self.client.get(self.download_url)
        self.client.logout()

        self.client.login(username=self.user_in_same_org.username, password='password123')
        self.client.get(self.download_url)

        self._test_download_count(1)

    def test_different_users_in_same_org_downloading(self):
        self.client.login(username=self.uploading_user.username, password='password123')
        self.client.get(self.download_url)
        self.client.logout()

        self.client.login(username=self.user_in_same_org.username, password='password123')
        self.client.get(self.download_url)

        self._test_download_count(2)

    def _test_download_count(self, download_count: int):
        response = self.client.get(self.organizations_url)
        organization = [org for org in response.data if org['id'] == self.organization_a.id][0]
        self.assertEqual(organization.get('download_count'), download_count)
