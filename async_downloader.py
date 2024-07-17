import aiohttp
import asyncio
import hashlib
import os
import tempfile
from bs4 import BeautifulSoup


async def get_all_file_urls(session, repo_url):
    async with session.get(repo_url) as resp:
        html_content = await resp.text()

    soup = BeautifulSoup(html_content, 'lxml')
    links = soup.find_all('a', href=True)
    file_links = []
    for link in links:
        href = link['href']
        # Фильтрация только txt файлов
        if href.endswith('.txt'):
            file_links.append(href)
    return file_links


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

async def calculate_sha256_for_file(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

async def main(repo_url):
    async with aiohttp.ClientSession() as session:
        try:
            file_urls = await get_all_file_urls(session, repo_url)
            download_tasks = [download_file(session, url) for url in file_urls]
            downloaded_files = await asyncio.gather(*download_tasks)
            sha256_hashes = [calculate_sha256_for_file(file) for file in downloaded_files]
            return sha256_hashes
        except Exception as e:
            print(f"Error processing {repo_url}: {e}")

if __name__ == "__main__":
    repo_url = "https://gitea.radium.group/radium/project-configuration"
    asyncio.run(main(repo_url))
