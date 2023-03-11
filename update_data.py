import requests
from bs4 import BeautifulSoup as bs
import json

all_movies  = [['https://www.thenetnaija.net/videos/series/page/2','Series'],['https://www.thenetnaija.net/videos/kdrama/page/2','kdrama']]


for series in all_movies:
    html = requests.get(series[0]).text
    soup = bs(html,'lxml')

    page_number = soup.find('ul',{'class':'pagination'}).find_all('li')[-2].text


    data = []
    for i in range(1,int(page_number)+1):
        link = f"https://www.thenetnaija.net/videos/series/page/{i}"
        page_html = requests.get(link)
        page_soup = bs(page_html.text,'lxml')
        
        all_page_movies = page_soup.find_all('article',{'class':'file-one shadow'})
        for j in all_page_movies: 
            a = j.find('a')
            title = a.text
            link = a['href']
            span = j.find('div',{'class':'inner'}).find_all('span')
            time_up = span[0]['title']
            num_of_commemt = int(span[1].text.strip())
            data.append({'title':title,'link':link,'time':time_up,'comment':num_of_commemt})
        



    with open(series[1], 'w') as fout:
        json.dump(data, fout)