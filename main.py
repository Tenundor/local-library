from pathlib import Path
import requests
from urllib.parse import urlparse


def download_file(file_url, file_path):
    file_path = Path(file_path)
    Path(file_path.parent).mkdir(parents=True, exist_ok=True)
    response = requests.get(file_url, verify=False)
    response.raise_for_status()
    file_path.write_bytes(response.content)


def main():
    for book_id in range(1, 11):
        file_url = f'https://tululu.org/txt.php?id={book_id}'
        book_name = f'books/{book_id}.txt'
        download_file(file_url, book_name)


if __name__ == "__main__":
    main()
