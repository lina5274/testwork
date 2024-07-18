"""Script to download and hash repository contents."""

import asyncio
import hashlib
import os
import tempfile
from typing import List, Tuple
import aiofiles
import aiohttp
import nest_asyncio
from aiohttp import ClientSession, ClientResponseError

API_URL = 'https://gitea.radium.group/api/v1'
REPO_OWNER = 'radium'
REPO_NAME = 'project-configuration'
MAX_CONCURRENT_TASKS = 3


async def fetch_file_list(session: ClientSession) -> List[dict]:
    """Fetch the list of files in the repository."""
    url = f'{API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/contents'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            files = await response.json()
            return [file for file in files if file['type'] == 'file']
    except ClientResponseError as e:
        print(f"Error fetching file list: {e}")
        return []


async def download_file(session: ClientSession, file_info: dict, temp_dir: str) -> str:
    """Download a single file from the repository."""
    url = file_info['download_url']
    local_path = os.path.join(temp_dir, file_info['path'])
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    try:
        async with session.get(url) as response:
            response.raise_for_status()
            async with aiofiles.open(local_path, mode='wb') as file:
                await file.write(await response.read())
        return local_path
    except ClientResponseError as e:
        print(f"Error downloading file {file_info['path']}: {e}")
        return ""


async def calculate_sha256(file_path: str) -> Tuple[str, str]:
    """Calculate SHA256 hash of a file."""
    if not file_path:
        return "", ""
    async with aiofiles.open(file_path, mode='rb') as file:
        file_hash = hashlib.sha256()
        chunk = await file.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = await file.read(8192)
    return file_path, file_hash.hexdigest()


async def process_file(session: ClientSession, file_info: dict, temp_dir: str) -> Tuple[str, str]:
    """Process a single file: download and calculate hash."""
    local_path = await download_file(session, file_info, temp_dir)
    return await calculate_sha256(local_path)


async def main() -> None:
    """Main function to orchestrate the download and hashing process."""
    with tempfile.TemporaryDirectory() as temp_dir:
        async with aiohttp.ClientSession() as session:
            file_list = await fetch_file_list(session)

            if not file_list:
                print("No files found or error occurred while fetching file list.")
                return

            semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

            async def bounded_process_file(file_info: dict) -> Tuple[str, str]:
                async with semaphore:
                    return await process_file(session, file_info, temp_dir)

            tasks = [bounded_process_file(file_info) for file_info in file_list]

            for completed in asyncio.as_completed(tasks):
                file_path, file_hash = await completed
                if file_path and file_hash:
                    print(f'SHA256 for {file_path}: {file_hash}')


if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
    
