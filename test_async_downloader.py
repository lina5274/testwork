import unittest
from unittest.mock import AsyncMock
import hashlib
import os
from async_downloader import fetch_file_list, download_file, calculate_sha256, process_file

class TestGiteaDownloader(unittest.TestCase):
    async def mock_get_response(self, status_code=200, content=None):
        class MockResponse:
            @staticmethod
            async def text():
                return content if content else ''
            @staticmethod
            async def json():
                return {'type': 'file', 'name': 'example.txt', 'path': '/example.txt'}
            async def raise_for_status(self):
                if status_code != 200:
                    raise ClientResponseError(None, None, reason="Mocked error")
        return MockResponse()

    async def mock_session(self):
        return AsyncMock(spec=aiohttp.ClientSession, get=self.mock_get_response)

    async def test_fetch_file_list(self):
        session = self.mock_session()
        result = await fetch_file_list(session)
        assert len(result) > 0
        assert result[0]['type'] == 'file'

    async def test_download_file(self):
        session = self.mock_session()
        file_info = {"download_url": "http://example.com/example.txt", "path": "/example.txt"}
        temp_dir = "/tmp/test"
        result = await download_file(session, file_info, temp_dir)
        assert os.path.exists(result)

    async def test_calculate_sha256(self):
        file_path = "/tmp/test/example.txt"
        result = await calculate_sha256(file_path)
        assert result[1] == hashlib.sha256(b"").hexdigest()

    async def test_process_file(self):
        session = self.mock_session()
        file_info = {"download_url": "http://example.com/example.txt", "path": "/example.txt"}
        temp_dir = "/tmp/test"
        result = await process_file(session, file_info, temp_dir)
        assert result[0] == file_info["path"]
        assert result[1] == hashlib.sha256(b"").hexdigest()  # Поскольку файл пустой

if __name__ == '__main__':
    unittest.main()
