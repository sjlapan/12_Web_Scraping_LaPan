from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pymongo
import time 
import pandas as pd

# Necessary base URLS for scraping

nasa_mars_base_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
jpl_image_base_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
mars_weather_twitter_base_url = "https://twitter.com/marswxreport?lang=en" 
mars_facts_base_url = "https://space-facts.com/mars/"
usgs_astro_base_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

# Response variables for Twitter

twitter_response = requests.get(mars_weather_twitter_base_url)

# def init_browser():
#     executable_path = {'executable_path': 'D:/DU_Bootcamp/code/12_Web_Scraping_LaPan/resources/chromedriver.exe'}
#     return Browser("chrome", **executable_path, headless=False)

def scrape():
    executable_path = {'executable_path': 'D:/DU_Bootcamp/code/12_Web_Scraping_LaPan/resources/chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    mars_data = {}

    # Scrape NASA page for first article
    
    time.sleep(3)
    browser.visit(nasa_mars_base_url)
    time.sleep(3)
    html = browser.html
    soup = bs(html, 'html.parser')

    title_tag = soup.select("div.content_title")[0]
    mars_data["NASA_article_title"] = title_tag.text
    print("got NASA title")
    description_tag = soup.select("div.article_teaser_body")[0]
    mars_data["NASA_article_text"] = description_tag.text
    print("got NASA text")
    
    # Scrape JPL

    time.sleep(3)
    browser.visit(jpl_image_base_url)
    time.sleep(5)
    html = browser.html
    soup = bs(html, 'html.parser')
    browser.click_link_by_partial_text("FULL IMAGE")
    time.sleep(4)
    image_tag = soup.find("a", class_="button fancybox")
    image_url_partial = image_tag["data-fancybox-href"]
    jpl_base_url = jpl_image_base_url.split("/spaceimages")[0]
    mars_data["jpl_image_url"] = jpl_base_url + image_url_partial
    print("got jpl image url")

    # Scrape Twitter

    twitter_soup = bs(twitter_response.text, "html.parser")
    mars_data["Mars_weather_tweet"] = twitter_soup.find("div", class_="js-tweet-text-container").text
    print("got the twitter data")

    # Scrape Mars Facts

    tables = pd.read_html(mars_facts_base_url)
    mars_df = tables[0]
    mars_df.columns = ["", "Value"]
    mars_df.set_index("", inplace = True)
    mars_data["facts_table_html"] = mars_df.to_html()
    print("Got the table HTML")

    # Scrape hemisphere images

    hemispheres = ["Cerberus", "Schiaparelli", "Syrtis", "Valles"]
    hemisphere_partial_urls = []

    browser.visit(usgs_astro_base_url)
    time.sleep(3)
    for hemisphere in hemispheres:
        try:
            browser.click_link_by_partial_text(hemisphere)
            time.sleep(3)
            browser.click_link_by_partial_text("Open")
            time.sleep(3)

            html = browser.html
            soup = bs(html, 'html.parser')
            image_data = soup.find("img", class_="wide-image")
            img_link = image_data["src"]
            hemisphere_partial_urls.append(img_link)
            print(img_link)
            # Reset to homepage
            browser.visit(usgs_astro_base_url)
            time.sleep(3)
        except:
            print("Something went wrong")
    browser.quit
    print("ran the hemisphere loop successfully")
    base_usgs_image_irl = usgs_astro_base_url.split("/search")[0]
    mars_data["full_cerberus_url"] = base_usgs_image_irl + hemisphere_partial_urls[0]
    mars_data["full_schiaparelli_url"] = base_usgs_image_irl + hemisphere_partial_urls[1]
    mars_data["full_syrtis_url"] = base_usgs_image_irl + hemisphere_partial_urls[2]
    mars_data["full_valles_url"] = base_usgs_image_irl + hemisphere_partial_urls[3]
    print("scraped the hemisphere image urls")

    return mars_data