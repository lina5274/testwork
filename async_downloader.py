import aiohttp
import asyncio
import hashlib
import os
import tempfile
import re

async def get_repo_files(session, repo_url):
    async with session.head(repo_url) as resp:
        if resp.status != 200:
            raise Exception("Failed to fetch repository files")
        content_disposition = resp.headers.get('Content-Disposition')
        if content_disposition:
            match = re.search(r'filename="(.*?)"', content_disposition)
            if match:
                return match.group(1)
        else:
            raise Exception("No Content-Disposition header found")

async def download_file(session, url):
    filename = os.path.join(tempfile.gettempdir(), url.split('/')[-1])
    async with session.get(url) as resp:
        with open(filename, 'wb') as f_handle:
            while True:
                chunk = await resp.content.read(1024)
                if not chunk:
                    break
                f_handle.write(chunk)
    return filename

async def main(repo_url):
    async with aiohttp.ClientSession() as session:
        try:
            file_url = await get_repo_files(session, repo_url)
            file_path = await download_file(session, file_url)
            sha256_hash = calculate_sha256(file_path)
            return sha256_hash
        except Exception as e:
            print(f"Error processing {repo_url}: {e}")

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    repo_url = "https://gitea.radium.group/radium/project-configuration"
    asyncio.run(main(repo_url))
