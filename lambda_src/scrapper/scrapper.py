from lambda_src.common_deps.service.logging import logger

from bs4 import BeautifulSoup
from pip._vendor import urllib3

from lambda_src.common_deps.model.Movie import Movie
from lambda_src.common_deps.model.exception import ScrappingError



def get_page(url):
    req = urllib3.PoolManager()
    res = req.request('GET', url)
    return res.data


def extract_data(body):
    try:
        movies_data = []
        soup = BeautifulSoup(body, 'html.parser')
        table = soup.find('table', attrs={'class': 'movieTable'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            movies_data.append(parse_movie_data(row))
        return movies_data
    except Exception as e:
        logger.error(e)
        logger.debug("Raising a scrapping exception")
        raise ScrappingError("Couldn't scrap the page")


def parse_movie_data(row):
    cols = row.find_all('td')
    content = [ele.text.strip() for ele in cols]
    return map_movie_data(content)


def map_movie_data(movie_data):
    return Movie(id=movie_data[0], primaryTitle=movie_data[1], originalTitle=movie_data[2], isAdult=movie_data[3],
                 startYear=movie_data[4], runtimeMinutes=movie_data[5], genres=movie_data[6]).to_dict()
