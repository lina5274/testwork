import unittest
from unittest.mock import AsyncMock
import hashlib
import os
from async_downloader import fetch_file_list, download_file, calculate_sha256, process_file
from aiohttp import ClientResponseError

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

    async def test_fetch_file_list_error_handling(self):
        session = self.mock_session(status_code=404)  # Имитация ошибки 404
        with self.assertRaises(ClientResponseError):  # Ожидаемое исключение
            await fetch_file_list(session)

    async def test_fetch_file_list_success(self):
        session = self.mock_session(status_code=200)
        files = await fetch_file_list(session)
        assert isinstance(files, list)
        assert len(files) > 0
        assert files[0]['type'] == 'file'

    async def test_download_file_error_handling(self):
        session = self.mock_session(status_code=404)  # Имитация ошибки 404
        file_info = {"download_url": "http://example.com/example.txt", "path": "/example.txt"}
        temp_dir = "/tmp/test"
        with self.assertRaises(ClientResponseError):  # Ожидаемое исключение
            await download_file(session, file_info, temp_dir)

    async def test_process_file_success(self):
        session = self.mock_session()
        file_info = {"download_url": "http://example.com/example.txt", "path": "/example.txt"}
        temp_dir = "/tmp/test"
        await download_file(session, file_info, temp_dir)
        result = await calculate_sha256(os.path.join(temp_dir, file_info['path']))
        expected_hash = hashlib.sha256(b"This is a test file.").hexdigest()
        assert result[1] == expected_hash


    async def test_process_file_success(self):
        session = self.mock_session()
        file_info = {"download_url": "http://example.com/example.txt", "path": "/example.txt"}
        temp_dir = "/tmp/test"
        await download_file(session, file_info, temp_dir)
        result = await calculate_sha256(os.path.join(temp_dir, file_info['path']))
        expected_hash = hashlib.sha256(b"This is a test file.").hexdigest()
        assert result[1] == expected_hash

    async def test_calculate_sha256_empty_file(self):
        file_path = "/tmp/test/example.txt"
        result = await calculate_sha256(file_path)
        assert result[1] == hashlib.sha256(b"").hexdigest()

    async def test_calculate_sha256_nonexistent_file(self):
        file_path = "/tmp/test/nonexistent_file.txt"
        with self.assertRaises(FileNotFoundError):
            await calculate_sha256(file_path)

    async def test_calculate_sha256_non_empty_file(self):
        file_content = b"This is a test file."
        file_path = "/tmp/test/example.txt"
        with open(file_path, "wb") as file:
            file.write(file_content)
        result = await calculate_sha256(file_path)
        expected_hash = hashlib.sha256(file_content).hexdigest()
        assert result[1] == expected_hash

    async def test_process_file(self):
        session = self.mock_session()
        file_info = {"download_url": "http://example.com/example.txt", "path": "/example.txt"}
        temp_dir = "/tmp/test"
        result = await process_file(session, file_info, temp_dir)
        assert result[0] == file_info["path"]
        assert result[1] == hashlib.sha256(b"").hexdigest()  # Поскольку файл пустой

if __name__ == '__main__':
    unittest.main()
