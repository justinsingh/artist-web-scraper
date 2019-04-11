# ----------------------------------------------------------------------

# Program:     National Gallery of Art Web Scraper
# Purpose:     Use BeautifulSoup and the Wikipedia API to create a
#              .csv file logging information on artists from the
#               national gallery of art
#
# Author:       Justin Singh
#
# ----------------------------------------------------------------------
"""
Implements a web scraper for the website:
https://web.archive.org/web/20170131230332/https://www.nga.gov/collectio
n/an.shtm. This website links to 26 different list of artist names,
each one representing a last name beginning with a different letter.

This program also creates a .csv file locally, which contains each
artist name, link to their artist page, and wikipedia summary sentence.
"""
import csv
import string
import wikipedia
import requests
from bs4 import BeautifulSoup

def get_name_list(artist_list_url):
    """
    Use the given URL to return a list of all artist names included in the url

    :param artist_list_url: (string) url of where to find the list of
                            artist names
    :return: (list) string list of artist names
    """
    # page of the list of artists
    artists_page = requests.get(artist_list_url)

    # beautifulsoup object
    soup = BeautifulSoup(artists_page.text, features = 'html.parser')

    # decompose extra links in 'a' tags, which have an 'AlphaNav' tag
    extra_links = soup.find(class_ = 'AlphaNav')
    extra_links.decompose()

    # get text from BodyText div, which includes a table of artist names
    table_name_list = soup.find(class_ = 'BodyText')

    # get text from <a> tags within BodyText div, which includes the names
    artist_name_list = table_name_list.find_all('a')

    return artist_name_list

def write_data(file, name_list):
    """

    :param file: (csv file) csv file we are writing artist names, links,
                 and summaries to
    :param name_list: (list) list of artist names
    """
    # iterate over artists_names and write names and links to file
    for name in name_list:
        name_content = name.contents[0]
        link = 'https://web.archive.org' + name.get('href')

        # make version of name that follows a first name, last name order
        # so that we can search for the corresponding wikipedia summary
        list_first_last_name = name_content.split()

        # check for case where artist only has first name listed
        try:
            wiki_name = list_first_last_name[1] + " " + \
                        list_first_last_name[0].strip(string.punctuation)
        except IndexError:
            wiki_name = list_first_last_name[0].strip(string.punctuation)

        # check if artist has a wikipedia entry
        try:
            wiki_page = wikipedia.page(wiki_name)
            if wiki_page.title.lower() == wiki_name.lower() or check_if_artist(
                    wiki_page):
                wiki_summary = wiki_page.summary
            else:
                wiki_summary = "No Wikipedia Entry Available for this artist"
        except wikipedia.WikipediaException:
            wiki_summary = "No Wikipedia Entry Available for this artist"

        file.writerow([name_content, link, wiki_summary])

def check_if_artist(wiki_page):
    """
    Some artists will not have their name spelled the same on the
    national gallery of art website as they do on wikipedia. So, we will
    check if the top chosen wiki article when inputting their artist
    name is  in the category of art. If that's the case, we will return
    true.

    :param wiki_page: (wikipedia.page object) a wikipedia page
    :return: (bool) whether or not the given wiki page is of an artist
    """
    # keywords for artist categories
    keywords = {'art', 'artist', 'sculptor', 'painter'}
    list_of_categories = wiki_page.categories

    # check if any of words in each category have the word 'art' or 'artist'
    for category in list_of_categories:
        words = category.split()
        for word in words:
            if word.lower() in keywords:
                return True

    return False

def main():
    # setup csv file with top row headings: name, link, and wiki summary
    file = csv.writer(open('artist_data.csv', 'w'))
    file.writerow(['Name', 'Link', 'Wiki Summary'])

    # iterate through the alphabet to write data for each artist list
    for character in string.ascii_uppercase:
        artist_list_url = 'https://web.archive.org/web/20121007172955/https' \
                          '://www.nga.gov/collection/an' + character + '1.htm'
        name_list = get_name_list(artist_list_url)
        write_data(file, name_list)

if __name__ == '__main__':
    main()
