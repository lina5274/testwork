import pytest
from unittest.mock import patch, MagicMock
from async_downloader import main, download_file, calculate_sha256
import os


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_download_file(mock_get):
    mock_response = MagicMock()
    mock_response.content.read.return_value = b"test content"
    mock_get.return_value.__aenter__.return_value = mock_response

    file_path = await download_file("http://example.com")

    assert os.path.exists(file_path)
    assert calculate_sha256(file_path) == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

    # Удаление файла после теста
    os.remove(file_path)


@pytest.mark.asyncio
async def test_main():
    urls = ["http://example.com/file1.txt", "http://example.com/file2.txt", "http://example.com/file3.txt"]
    with patch('async_downloader.download_file', return_value="tempfile"):
        hashes = await main(urls)

    assert len(hashes) == len(urls)


@patch('builtins.open', new_callable=MagicMock)
def test_calculate_sha256(mock_open):
    mock_file = MagicMock(spec=file)
    mock_open.return_value.__enter__.return_value = mock_file

    # Имитация чтения файла
    mock_file.read.side_effect = [b"test content", b""]

    # Вызов тестируемой функции
    hash_value = calculate_sha256("test.txt")

    assert hash_value == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"