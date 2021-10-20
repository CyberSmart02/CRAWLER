from bs4 import BeautifulSoup
import requests
import pymongo
import urllib.parse
import sys

class Crawler():

    connection_url = "mongodb://127.0.0.1:27017/"

    client = pymongo.MongoClient(connection_url)

    db = client.info

    disallowed_links = []

    def start_crawl(self, url, depth):
        robots_url = urllib.parse.urljoin(url, '/robots.txt')

        try:
            robots = requests.get(robots_url)
        except:
            print("No Robots found!!!")
            self.crawl(url, depth)

        soup = BeautifulSoup(robots.text, 'lxml')

        content = soup.find('p').text

        for word in content:
            if word[0] == '/':
                self.disallowed_links.append(urllib.parse.urljoin(url, word))

        print("robots found and appended in disallowed_links")

        self.crawl(url, depth, self.disallowed_links)

    def crawl(self, url, depth, disallowed_links):

        try:
            print(f"Crawling url {url} at depth: {depth}")
            response = requests.get(url)
        except:
            print(f"Failed to perform HTTP GET request on {url}")
            return

        soup = BeautifulSoup(response.text, 'lxml')

        try:
            title = soup.find('title').text
            desc = ''

            for tag in soup.findAll():
                if tag.name == 'p':
                    desc += tag.text.strip().replace('\n', '')

        except:
            print("Failed to retrieve title and description")
            return

        query = {
            'url': url,
            'title': title,
            'description': desc,
        }

        search_info = self.db.search_info

        search_info.insert_one(query)

        search_info.create_index(
            [
                ('url', pymongo.TEXT),
                ('title', pymongo.TEXT),
                ('description', pymongo.TEXT)
            ],
            name='search_results',
            default_language="english"
        )


        links = []
        if depth==0:
                return
        else :
                for Link in soup.find_all('a'):
                    links.append(Link.get('href'))
        for link in links:
                if link in disallowed_links:
                    print('Disallowed link encountered.')
                else:
                    self.crawl(link, depth-1)

        self.client.close()

object = Crawler()
object.start_crawl('https://www.geeksforgeeks.org/', 1)

#Links:
#https://www.geeksforgeeks.org/
#https://www.rottentomatoes.com/
#https://www.stackoverflow.com/
#https://www.wikipedia.org/