from unittest import TestCase
from unittest import mock

import requests

from image_downloader import ImageDownloader, get_urls_from_file, DownloadError


class TestImageDownloader(TestCase):
    def setUp(self):
        self.response = requests.Response()
        self.response._content = 'image content data'
        self.response.status_code = 200
        request_patcher = mock.patch('image_downloader.requests')
        self.requests_mock = request_patcher.start()
        self.addCleanup(request_patcher.stop)
        self.requests_mock.get.return_value = self.response

        is_file_patcher = mock.patch('image_downloader.isfile')
        self.is_file_mock = is_file_patcher.start()
        self.addCleanup(is_file_patcher.stop)
        self.is_file_mock.side_effect = [False]

        open_patcher = mock.patch('image_downloader.open')
        self.mock_open = open_patcher.start()
        self.addCleanup(open_patcher.stop)

    def assert_file_saved(self, name, data):
        self.mock_open.assert_called_once_with(name, 'wb')
        f = self.mock_open.return_value.__enter__.return_value
        f.write.assert_called_once_with(data)

    def test_get_image_returns_image_content(self):
        name, image = ImageDownloader.get_image('http://domain.com/image.png')
        assert image == self.response.content
        assert name == 'image.png'

    def test_get_image_returns_none_if_response_code_not_200(self):
        self.response.status_code = 404
        with self.assertRaises(DownloadError):
            ImageDownloader.get_image('http://domain.com/image.png')

    def test_file_is_saved(self):
        ImageDownloader.save('image.png', 'image data')
        self.assert_file_saved('image.png', 'image data')

    def test_suffix_is_added_to_file_name_if_already_exists(self):
        self.is_file_mock.side_effect = [True, True, True, False]
        ImageDownloader.save('image.png', 'image data')
        self.assert_file_saved('image-3.png', 'image data')

    def test_download_images(self):
        ImageDownloader.download(['http://domain.com/image.png'])
        self.assert_file_saved('image.png', 'image content data')


@mock.patch('image_downloader.open')
def test_get_urls_from_file(mock_open):
    urls = get_urls_from_file('urls.txt')

    f = mock_open.return_value.__enter__.return_value
    assert urls == f.readlines.return_value

    mock_open.assert_called_once_with('urls.txt', 'r')
    f.readlines.assert_called_once_with()
