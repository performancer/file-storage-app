from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from downloads.models import Download
from files.tests import FileTestingHelper
from organizations.models import Organization

User = get_user_model()


# The users should ... be able to download any of the uploaded files from any organization.
class TestDownload(APITestCase):
    def setUp(self):
        # populate the organizations
        organization_a = Organization.objects.create(name='organization_a')
        organization_b = Organization.objects.create(name='organization_b')

        # populate users
        self.uploading_user = User.objects.create_user(
            username='uploading_user',
            password='password123',
            organization=organization_a,
        )
        self.user_in_same_org = User.objects.create_user(
            username='user_in_same_org',
            password='password123',
            organization=organization_a,
        )
        self.user_in_external_org = User.objects.create_user(
            username='user_in_external_org',
            password='password123',
            organization=organization_b,
        )

        # prepare the api
        self.client = APIClient()
        self.files_url = '/files/'
        self.uploaded_file_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.uploading_user.username,
            password='password123',
        )
        self.download_url = f'/download/{self.uploaded_file_id}'

    def test_download_as_uploader(self):
        self.client.login(username=self.uploading_user, password='password123')
        response = self.client.get(self.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_as_same_org(self):
        self.client.login(username=self.user_in_same_org.username, password='password123')
        response = self.client.get(self.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_as_external_org(self):
        self.client.login(username=self.user_in_external_org.username, password='password123')
        response = self.client.get(self.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_as_anonymous_user(self):
        response = self.client.get(self.download_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# Each download should be recorded
class TestDownloadsRecording(APITestCase):
    def setUp(self):
        # populate users and organizations
        self.organization = Organization.objects.create(name='organization_a')
        self.user = User.objects.create_user(username='user_a', password='password123', organization=self.organization)

        # prepare the api
        self.client = APIClient()
        self.files_url = '/files/'
        self.uploaded_file_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.user.username,
            password='password123',
        )
        self.download_url = f'/download/{self.uploaded_file_id}'

    def test_no_downloads(self):
        count = Download.objects.filter(file=self.uploaded_file_id).count()
        self.assertEqual(count, 0)

    def test_download_recording(self):
        self.client.login(username=self.user.username, password='password123')
        self.client.get(self.download_url)
        obj = Download.objects.get(file=self.uploaded_file_id)

        # check that the file, user and organization are correct
        self.assertEqual(obj.file.id, self.uploaded_file_id)
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.organization, self.organization)

    def test_download_recording_multiple(self):
        self.client.login(username=self.user.username, password='password123')
        self.client.get(self.download_url)
        self.client.get(self.download_url)
        download_count = Download.objects.filter(file=self.uploaded_file_id).count()

        self.assertEqual(download_count, 2)


# Endpoint for listing all downloads (file, timestamp) done by a single user.
class TestDownloadsPerUser(APITestCase):
    def setUp(self):
        # populate the organizations
        organization = Organization.objects.create(name='organization')

        # populate users
        self.user_a = User.objects.create_user(username='user_a', password='password123', organization=organization)
        self.user_b = User.objects.create_user(username='user_b', password='password123', organization=organization)

        # prepare the api
        self.client = APIClient()
        self.files_url = '/files/'
        self.uploaded_file_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.user_a.username,
            password='password123',
        )
        self.download_url = f'/download/{self.uploaded_file_id}'
        self.downloads_per_user_url = f'/downloads/user/{self.user_a.id}'

    def test_anonymous_user(self):
        response = self.client.get(self.downloads_per_user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_downloads(self):
        self.client.login(username=self.user_a.username, password='password123')
        response = self.client.get(self.downloads_per_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_download_data(self):
        self.client.login(username=self.user_a.username, password='password123')
        self.client.get(self.download_url)

        response = self.client.get(self.downloads_per_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that it contains file and timestamp
        self.assertIsNotNone(response.data[0].get('file'))
        self.assertIsNotNone(response.data[0].get('downloaded_at'))

    def test_multiple_downloads(self):
        self.client.login(username=self.user_a.username, password='password123')
        self.client.get(self.download_url)
        self.client.get(self.download_url)

        response = self.client.get(self.downloads_per_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_no_other_user_downloads_included(self):
        self.client.login(username=self.user_b.username, password='password123')
        self.client.get(self.download_url)
        self.client.logout()

        self.client.login(username=self.user_a.username, password='password123')
        self.client.get(self.download_url)

        # make sure that another user downloading files does not affect the other
        response = self.client.get(self.downloads_per_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


# Endpoint for listing all downloads (user, timestamp) for a single file
class TestDownloadsPerFile(APITestCase):
    def setUp(self):
        # populate the organizations
        organization = Organization.objects.create(name='organization')

        # populate users
        self.user_a = User.objects.create_user(username='user_a', password='password123', organization=organization)
        self.user_b = User.objects.create_user(username='user_b', password='password123', organization=organization)

        # prepare the api
        self.client = APIClient()
        self.files_url = '/files/'
        self.uploaded_file_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.user_a.username,
            password='password123',
        )
        self.download_url = f'/download/{self.uploaded_file_id}'
        self.downloads_per_file_url = f'/downloads/file/{self.uploaded_file_id}'

    def test_anonymous_user(self):
        response = self.client.get(self.downloads_per_file_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_downloads(self):
        self.client.login(username=self.user_a.username, password='password123')
        response = self.client.get(self.downloads_per_file_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_download_data(self):
        self.client.login(username=self.user_a.username, password='password123')
        self.client.get(self.download_url)

        response = self.client.get(self.downloads_per_file_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that it contains file and timestamp
        self.assertIsNotNone(response.data[0].get('file'))
        self.assertIsNotNone(response.data[0].get('downloaded_at'))

    def test_multiple_downloads(self):
        self.client.login(username=self.user_a.username, password='password123')
        self.client.get(self.download_url)
        self.client.get(self.download_url)

        response = self.client.get(self.downloads_per_file_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_no_other_file_downloads_included(self):
        self.client.login(username=self.user_a.username, password='password123')
        self.client.get(self.download_url)
        self.client.logout()

        # upload and download a second file
        self.second_uploaded_file_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.user_a.username,
            password='password123',
        )

        self.client.login(username=self.user_a.username, password='password123')
        self.client.get(f'/download/{self.second_uploaded_file_id}')

        # make sure dealing with another file does not affect the downloads of the first file
        response = self.client.get(self.downloads_per_file_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
