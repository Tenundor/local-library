from pathlib import Path

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


def parse_book_page(page):
    soup = BeautifulSoup(page, 'lxml')
    title_author_tag = soup.find('td', class_='ow_px_td').find('h1')
    title_author_text = title_author_tag.text.split('::')
    return {
        'title': title_author_text[0].strip(),
        'author': title_author_text[1].strip(),
    }


def download_txt(url, filename, folder='books/'):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    filename = sanitize_filename(filename)
    filepath = Path(folder) / filename
    Path(filepath.parent).mkdir(parents=True, exist_ok=True)
    filepath.write_bytes(response.content)
    return str(filepath)


def check_for_redirect(response):
    redirection_codes = range(300, 309)
    for old_response in response.history:
        if old_response.status_code in redirection_codes:
            raise requests.HTTPError


def main():
    for book_id in range(1, 11):
        book_page_url = f'https://tululu.org/b{book_id}/'
        book_file_url = f'https://tululu.org/txt.php?id={book_id}'
        try:
            book_page_response = requests.get(book_page_url, verify=False)
            book_page_response.raise_for_status()
            check_for_redirect(book_page_response)
            book_name = parse_book_page(book_page_response.text)['title']
            book_file_name = f'{book_id}.{book_name}.txt'
            print(download_txt(book_file_url, book_file_name))
        except requests.HTTPError:
            continue


if __name__ == "__main__":
    main()
