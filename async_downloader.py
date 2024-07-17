import aiohttp
import asyncio
import hashlib
import os
import tempfile

async def download_file(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                filename = os.path.join(tempfile.gettempdir(), url.split('/')[-1])
                with open(filename, 'wb') as f_handle:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f_handle.write(chunk)
                return filename
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def calculate_sha256(file_path):
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path,"rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating SHA256 for {file_path}: {e}")
        return None

async def main(urls):
    download_tasks = [download_file(url) for url in urls]
    downloaded_files = await asyncio.gather(*download_tasks)
    sha256_hashes = [calculate_sha256(file) for file in downloaded_files if file]
    return sha256_hashes

if __name__ == "__main__":
    urls = [
        "https://gitea.radium.group/radium/project-configuration/file1.txt",
        "https://gitea.radium.group/radium/project-configuration/file2.txt",
        "https://gitea.radium.group/radium/project-configuration/file3.txt",
    ]
    asyncio.run(main(urls))