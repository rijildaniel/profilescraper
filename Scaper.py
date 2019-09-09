"""
------------------------Scrapying the Facebook's Public Profiles - (Info)-------------------------
"""

import requests
from bs4 import BeautifulSoup
import os
import re
import pickle
import json


def FacebookScaper(url, fname='profiles'):
    profile_fname = fname+".json"
    i = None
    urls = None
    visited_links = []
    profile_list = []
    print("----Exit the program by pressing Ctrl-C----")
    try:
        search = url
        '''
            Profiles file is to store the profiles scraped in which profiles are separated by a ;;; separator
        '''
        if os.path.isfile(profile_fname):
            profiles = open(profile_fname, 'r')
            profile_list = json.load(profiles)

        '''
           To start scraping the contents from links where it was stopped 
        '''
        if os.path.isfile('links'):
            with open('links', 'rb') as links_file:
                urls, visited_links, i = pickle.load(links_file)
        else:
            urls = [search]
            i = 0

        unsuccess = 0
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        while True:
            if urls[i] not in visited_links:
                page = requests.get(urls[i], headers=headers)
            else:
                i += 1
                continue

            if page.status_code == 200:
                unsuccess = 0
                print(urls[i])
                contents = BeautifulSoup(page.content, "html.parser")

                info = {}
                name = contents.find('a', {'class': '_51sx'})
                '''Scrape the name of the person'''
                if name is not None:
                    name = name.get_text(separator='\n')
                    name = str(name).replace('About ', '')
                    info['name'] = name
                eduwork = contents.find('div', {'id': 'pagelet_eduwork'})
                '''Scrape the education and work of a person'''
                if eduwork is not None:
                    eduwork = eduwork.get_text(separator='\n')
                    info['eduNwork'] = eduwork
                else:
                    info['eduNwork'] = None
                place = contents.find('div', {'id': 'pagelet_hometown'})
                '''Scrape the place of a person'''
                if place is not None:
                    place = place.get_text(separator='\n')
                    info['place'] = place
                else:
                    info['place'] = None

                profile_list.append(info)
                other_profiles_link = contents.find_all('a', {'class': '_8o _8t lfloat _ohe', 'href': re.compile("^https://")})
                for link in other_profiles_link:
                    urls.append(link.get('href'))
                visited_links.append(urls[i])
                i += 1
            else:
                unsuccess += 1
                if unsuccess == 5:
                    raise Exception("Connection problem with server Try again some time later.....")
                continue
            if i == len(urls):
                break

    except KeyboardInterrupt:
        print("\nStopped scarping...........\nStart scraping again by just rerunning the program")
    except IndexError as e:
        i -= 1
        print("\nSite Blocked You.....................\nTry again some time later............")
    except Exception as e:
        print(e)

    finally:
        with open('links', 'wb') as links_file:
            pickle.dump([urls, visited_links, i], links_file)
        with open(profile_fname, 'w') as profiles:
            json.dump(profile_list, profiles)
        print("\nSuccessfully saved the state.......")


if __name__ == "__main__":
    FacebookScaper("https://www.facebook.com/rijo.daniel.796", 'profiles')