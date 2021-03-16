import argparse
from pathlib import Path
import urllib3
from urllib.parse import urljoin, urlsplit, unquote

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


def find_filename_in_url(file_url):
    path = Path(urlsplit(file_url).path)
    return unquote(path.name)


def parse_book_page(page, baseurl='https://tululu.org/'):
    soup = BeautifulSoup(page, 'lxml')
    title_author_tag = soup.find('td', class_='ow_px_td').find('h1')
    title, author = title_author_tag.text.split('::')
    relative_img_url = soup.find('div', class_='bookimage').find('img')['src']
    comments_tags = soup.find_all('div', class_='texts')
    genres_tags = soup.find('span', class_='d_book').find_all('a')
    return {
        'title': title.strip(),
        'author': author.strip(),
        'img_url': urljoin(baseurl, relative_img_url),
        'img_filename': find_filename_in_url(relative_img_url),
        'comments': [comment.find('span').text for comment in comments_tags],
        'genres': [genre.text for genre in genres_tags],
    }


def get_response(url, **request_parameters):
    response = requests.get(url, verify=False, params=request_parameters)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def download_file(url, filename, folder='', **request_parameters):
    response = get_response(url, **request_parameters)
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


def create_parser():
    parser = argparse.ArgumentParser(
        description='Программа парсит книги с сайта tululu.org'
    )
    parser.add_argument('-s', '--start_id',
                        help='Начальный индекс книги из диапазона',
                        type=int, default=1)
    parser.add_argument('-e', '--end_id',
                        help='Конечный индекс книги из диапазона',
                        type=int, default=10)
    return parser


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = create_parser()
    args = parser.parse_args()
    library_url = 'https://tululu.org'
    for book_id in range(args.start_id, args.end_id + 1):
        book_page_url = f'{library_url}/b{book_id}/'
        try:
            book_page = get_response(book_page_url)
            parsed_book_page = parse_book_page(book_page.text)
            book_name = parsed_book_page['title']
            book_file_name = f'{book_id}.{book_name}.txt'
            img_url = parsed_book_page['img_url']
            img_filename = parsed_book_page['img_filename']
            download_file(img_url, img_filename, folder='images')
            download_file(library_url, book_file_name, 'books', id=book_id)
        except requests.HTTPError:
            continue


if __name__ == "__main__":
    main()
