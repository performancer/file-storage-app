from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from organizations.models import Organization
from users.models import OrganizationUser

User = get_user_model()

class FileTestingHelper:
    @staticmethod
    def upload_test_file(client: Client, files_url: str, username: str, password: str):
        # create a test file data
        test_file = SimpleUploadedFile(name='test_file.txt', content=b'Hello world', content_type='text/plain')

        # upload the test file
        client.login(username=username, password=password)
        response = client.post(files_url, {'file': test_file})
        client.logout()

        # return the id of the file
        return response.data['id']

# The users should be able to upload files.
# The uploaded file should belong to the same organization as the user that uploaded it.
class TestFileUpload(APITestCase):
    def setUp(self):
        # populate users
        self.user_with_org = User.objects.create_user(username='user_with_org', password='password123')
        self.user_without_org = User.objects.create_user(username='user_without_org', password='password123')

        # populate organizations
        self.organization = Organization.objects.create(name='test_organization')
        OrganizationUser.objects.create(user=self.user_with_org, organization=self.organization)

        # prepare the api
        self.client = APIClient()
        self.files_url = '/files/'

        # mock file to test with
        self.test_file = SimpleUploadedFile(name='test_file.txt', content=b'Hello world', content_type='text/plain')

    def test_user_with_org_can_upload_file(self):
        self.client.login(username=self.user_with_org.username, password='password123')

        # check that the user can upload
        response = self.client.post(self.files_url, {'file': self.test_file})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that the organization matches
        self.assertEqual(response.data.get('organization'), self.organization.name)

    def test_user_without_org_cannot_upload_file(self):
        self.client.login(username=self.user_without_org.username, password='password123')
        response = self.client.post(self.files_url, {'file': self.test_file})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_upload_file(self):
        response = self.client.post(self.files_url, {'file': self.test_file})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# Endpoint for listing all the files, ...
class TestFileList(APITestCase):
    def setUp(self):
        # populate users
        self.uploading_user = User.objects.create_user(username='uploading_user', password='password123')
        self.user_in_same_org = User.objects.create_user(username='user_in_same_org', password='password123')
        self.user_in_external_org = User.objects.create_user(username='user_in_external_org', password='password123')
        self.user_without_org = User.objects.create_user(username='user_without_org', password='password123')

        # populate the organizations
        self.organization_a = Organization.objects.create(name='organization_a')
        self.organization_b = Organization.objects.create(name='organization_b')
        OrganizationUser.objects.create(user=self.uploading_user, organization=self.organization_a)
        OrganizationUser.objects.create(user=self.user_in_same_org, organization=self.organization_a)
        OrganizationUser.objects.create(user=self.user_in_external_org, organization=self.organization_b)

        # prepare the api
        self.client = APIClient()
        self.files_url = '/files/'
        self.uploaded_file_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.uploading_user.username,
            password='password123'
        )

    def test_file_list_as_uploader(self):
        self._assert_file_list_visible(self.uploading_user)

    def test_file_list_as_same_org(self):
        self._assert_file_list_visible(self.user_in_same_org)

    def test_file_list_as_external_org(self):
        self._assert_file_list_visible(self.user_in_external_org)

    def test_file_list_as_user_without_org(self):
        self.client.login(username=self.user_without_org.username, password='password123')
        self._assert_file_list_forbidden()

    def test_file_list_as_anonymous_user(self):
        self._assert_file_list_forbidden()

    def _assert_file_list_visible(self, user):
        self.client.login(username=user.username, password='password123')

        # check the file list endpoint
        response = self.client.get(self.files_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # map an array with the file ids
        file_ids = [file_obj['id'] for file_obj in response.data]

        # check that the uploaded id is in there
        self.assertIn(self.uploaded_file_id, file_ids)

    def _assert_file_list_forbidden(self):
        response = self.client.get(self.files_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# ...listing all the files, including the number of how many times each individual file has been downloaded.
class TestFileListDownloads(APITestCase):
    def setUp(self):
        # populate users
        self.user = User.objects.create_user(username='user', password='password123')

        # populate the organizations
        organization = Organization.objects.create(name='organization')
        OrganizationUser.objects.create(user=self.user, organization=organization)

        # prepare the api
        self.client = APIClient()
        self.files_url = '/files/'

        # populate files
        self.file_a_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.user.username,
            password='password123',
        )
        self.file_a_download_url = f'/download/{self.file_a_id}'
        self.file_b_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.user.username,
            password='password123',
        )
        self.file_b_download_url = f'/download/{self.file_b_id}'

    def test_file_download_counts(self):
        self.client.login(username=self.user.username, password='password123')

        # download the files multiple times
        self.client.get(self.file_a_download_url)
        self.client.get(self.file_a_download_url)
        self.client.get(self.file_a_download_url)
        self.client.get(self.file_b_download_url)
        self.client.get(self.file_b_download_url)

        # fetch the download counts
        response = self.client.get(self.files_url)

        # map the results to a dictionary by the id
        files_by_id = {file_obj['id']: file_obj for file_obj in response.data}

        self.assertEqual(files_by_id[self.file_a_id].get('download_count'), 3)
        self.assertEqual(files_by_id[self.file_b_id].get('download_count'), 2)

# The users should see ... any of the uploaded files from any organization.
class TestFileDetails(APITestCase):
    def setUp(self):
        # populate users
        self.uploading_user = User.objects.create_user(username='uploading_user', password='password123')
        self.user_in_same_org = User.objects.create_user(username='user_in_same_org', password='password123')
        self.user_in_external_org = User.objects.create_user(username='user_in_external_org', password='password123')
        self.user_without_org = User.objects.create_user(username='user_without_org', password='password123')

        # populate the organizations
        self.organization_a = Organization.objects.create(name='organization_a')
        self.organization_b = Organization.objects.create(name='organization_b')
        OrganizationUser.objects.create(user=self.uploading_user, organization=self.organization_a)
        OrganizationUser.objects.create(user=self.user_in_same_org, organization=self.organization_a)
        OrganizationUser.objects.create(user=self.user_in_external_org, organization=self.organization_b)

        # prepare the api
        self.client = APIClient()
        self.files_url = '/files/'
        self.uploaded_file_id = FileTestingHelper.upload_test_file(
            client=self.client,
            files_url=self.files_url,
            username=self.uploading_user.username,
            password='password123'
        )
        self.file_detail_url = f'{self.files_url}{self.uploaded_file_id}'

    def test_file_details_as_uploader(self):
        self._assert_file_details_visible(self.uploading_user)

    def test_file_details_as_same_org(self):
        self._assert_file_details_visible(self.user_in_same_org)

    def test_file_details_as_external_org(self):
        self._assert_file_details_visible(self.user_in_external_org)

    def test_file_details_as_user_without_org(self):
        self.client.login(username=self.user_without_org.username, password='password123')
        self._assert_file_details_forbidden()

    def test_file_details_as_anonymous_user(self):
        self._assert_file_details_forbidden()

    def _assert_file_details_visible(self, user):
        self.client.login(username=user.username, password='password123')

        # check the file detail endpoint
        response = self.client.get(self.file_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that the data is correct
        self.assertEqual(response.data.get('id'), self.uploaded_file_id)
        self.assertEqual(response.data.get('owner'), self.uploading_user.username)
        self.assertEqual(response.data.get('organization'), self.organization_a.name)

        self.client.logout()

    def _assert_file_details_forbidden(self):
        response = self.client.get(self.file_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
