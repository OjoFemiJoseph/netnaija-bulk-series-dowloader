import logging
import json
import time
import random
import requests
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import streamlit as st

logging.basicConfig(level=logging.INFO)

def start_download(links):
    """
    Downloads files from a list of links using Selenium.
    
    Args:
    - links (list): A list of download links.
    """
    #webdriver has to be set to global because it is defined in a function, without that it loses autoatically when it
    #gets to the last line of the code
    global driver
    driver = webdriver.Chrome()
    for link in links:
        try:
            driver.get(link)
            time.sleep(2)
            #click that takes you to sabishare, it fails on first trial sometimes
            for i in range(3):
                try:
                    time.sleep(1)
                    netnaija_download_but = driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div/div[1]/main/article/div[1]/div/div/div[1]/a')
                    netnaija_download_but.click()
                    break
                except:
                    pass

            time.sleep(2)
            #find the download button on sabishare
            sabishare_download_but = driver.find_element(By.XPATH, '//*[@id="action-buttons-con"]/div/button')
            #this clicks it regardless of popup, manually you woould have to close the pop up to click download
            driver.execute_script('arguments[0].click();', sabishare_download_but)
            #close any tab might open from the action above
            working_tab = driver.current_window_handle
            for tab in driver.window_handles:
                driver.switch_to.window(tab)
                if tab != working_tab:
                    driver.close()
            time.sleep(2)
        except Exception as e:
            print(e)
    
def get_seasons(link):
    """
    Returns a dictionary of season names and links from a TV series page.
    
    Args:
    - link (str): A link to a TV series page.
    
    Returns:
    - season (dict): A dictionary of season names and links.
    """
    
    season_html = requests.get(link)
    season_soup = bs(season_html.text, 'lxml')
    season_tag = season_soup.find('div', {'class': 'video-seasons'})
    num_of_seasons = season_tag.find_all('div', {'class':"vs-one"})
    season = {i.find('a').text: i.find('a')['href'] for i in num_of_seasons}
    
    return season

def download_season(*args):
    """
    Downloads a season of a TV series.
    
    Args:
    - *args: A list of arguments passed from a Streamlit button.
    """
    st.write(f"Downloading...")
    spec_seson = requests.get(*args)
    season_ep_soup = bs(spec_seson.text, 'lxml')
    season_ep_tag = season_ep_soup.find('div', {'class': 'video-files'})
    num_of_seasons_ep = season_ep_tag.find_all('article', {'class': "file-one shadow"})
    season_ep = {i.find('a').text: i.find('a')['href'] for i in num_of_seasons_ep}
    st.write(len(season_ep))
    start_download(season_ep.values())


categories = ["Korean Series", "Hollywood", "Chinese", "Indian"]
filter_options = ["Alphabetical", "Number of comments", "Time"]

st.sidebar.title("Movie Categories")
selected_category = st.sidebar.selectbox("Select a category", categories)

st.sidebar.title("Sort by")
selected_filter = st.sidebar.selectbox("Select a filter", filter_options)

st.title("Movies")
st.write(f"Showing movies in {selected_category} category sorted by {selected_filter}")

if selected_category=='Korean Series':
    filename = 'kdrama'
else:
    filename = 'others'

with open(filename, 'r') as f:
    movie_list = json.load(f)

if selected_filter == "Alphabetical":
    movie_list = sorted(movie_list, key=lambda x: x["title"])
elif selected_filter == "Number of comments":
    movie_list = sorted(movie_list, key=lambda x: x["comment"], reverse=True)
else:
    movie_list = sorted(movie_list, key=lambda x: x["time"], reverse=True)


num_movies = len(movie_list)
items_per_page = 10
num_pages = num_movies // items_per_page 
page = st.slider("Select a page", 1, num_pages, 1)


start_index = (page - 1) * items_per_page
end_index = start_index + items_per_page

for movie in movie_list[start_index:end_index]:
    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        st.write(movie["comment"])
    with col2:
        if st.button(movie["title"], key=f"{movie['title']}"):
            
            seasons = get_seasons(movie["link"])
            st.write("Seasons:")
            for season,link in seasons.items():
                st.write(season)
                st.button("Download",key=f"{movie['title']}-{season}",on_click=download_season,args=[link])
                
