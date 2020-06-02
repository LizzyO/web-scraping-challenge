# Dependencies
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import time
import pandas as pd


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    #get mars title and paragraph
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    response = requests.get(url)
    time.sleep(1)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find('div', class_="slide")

    news_title = results.find('div', class_="content_title").text
    news_p = results.find('div', class_="rollover_description_inner").text

    #get mars featured image
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(3)
    browser.click_link_by_id('full_image')
    time.sleep(3)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    featured_image = soup.find('img', class_= "fancybox-image")
    featured_image_src = featured_image.get('src')
    featured_image_url = "https://www.jpl.nasa.gov"+ featured_image_src


    # Mars weather
    url= "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    time.sleep(3)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    results = soup.find('div', class_="css-1dbjc4n r-my5ep6 r-qklmqi r-1adg3ll")
    results_filtered = results.find_all('span', class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0")
    final_filter = results_filtered[4].text

    #Mars Facts
    url= "https://space-facts.com/mars/"
    #read the tables
    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['Description', 'Value']
    df.set_index('Description', inplace=True)

    #convert the table to HTML
    html_table = df.to_html()

    #clean it up by removing new lines
    html_table.replace('\n', '')


    #Mars Hemisphere's 
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    time.sleep(1)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    sidebar = soup.find_all('div', class_="item")
    hemisphere_image_urls = []

    main_url = 'https://astrogeology.usgs.gov'

    for section in sidebar:

        title = section.find('h3').text
        img_src= section.find('a', class_='itemLink product-item')['href']
        img_url = main_url + img_src 
         #visit page and parse again
        browser.visit(img_url)
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        full_image = soup.find('img', class_="wide-image")
        full_image_new = full_image.get('src')
        full_res_image = main_url + full_image_new
        hemisphere_image_urls.append({"title": title, "img_url": full_res_image})
    hemisphere_image_urls
    
    # Store data in a dictionary
    mars_data = {
    "mars_title": news_title,
    "mars_newsp": news_p,
    "jpl_image": featured_image_url,
    "mars_weather": final_filter,
    "mars_facts": html_table,
    "mars_hemispheres": hemisphere_image_urls
     }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data
