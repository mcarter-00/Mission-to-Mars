# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():
    # Inititate headless driver for deployment
    browser = Browser('chrome', executable_path='chromedriver', headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': featured_image(browser),
        'facts': mars_facts(),
        'hemisphere_images': hemispheres(browser),
        'last_modified': dt.datetime.now()
    }

    # End the session
    #browser.quit()
    
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('ul.item_list li.slide', wait_time=1)

    # Set up the HTML parser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    slide_elem = news_soup.select_one('ul.item_list li.slide')
    slide_elem.find('div', class_='content_title')
    
    # Use the parent element to find the first 'a' tag and save it as 'news_title'
    news_title = slide_elem.find('div', class_='content_title').get_text()
    
    # Use the parent element to find the paragraph text
    news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first 'a' tag and save it as 'news_title
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    # Find the relative image url
    img_url_rel = img_soup.select_one('figure.lede a img').get('src')

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    # Add try/except for error handling
    try: 
        #find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get('src')
    except AttributeError:
        return None

    return img_url

def mars_facts():
    
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[1]
    except BaseException:
        return None

    # Assign columns and set infex of dataframe
    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HMTL format, add bootstrap
    return df.to_html()

# CHALLENGE: Scrape the four Mars Hemisphere Images and Titles
def hemispheres(browser):

    # Visit the Mars Hemisphere site
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Click the link, find the sample image, get the sample image url
    sample_image_urls = []
    for i in range(4):
        browser.find_by_css('a.product-item h3')[i].click()
        links = scrape_hemisphere(browser.html)
        sample_image_urls.append(links)
        browser.back()
    
    for i in sample_image_urls:
        print(i['img_url'])

    return sample_image_urls

def scrape_hemisphere(html_text):

    # Parse through html text
    hemi_soup = BeautifulSoup(html_text, 'html.parser')

    # Add try/except for error handling
    try:
        title_elem = hemi_soup.find('h2', class_='title').get_text()
        sample_elem = hemi_soup.find('a', text='Sample').get('href')
    except AttributeError:
        title_elem = None
        sample_elem = None

    hemispheres = {
        'title': title_elem,
        'img_url': sample_elem
    }

    return hemispheres

if __name__ == '__main__':
    # If running as script, print scraped data
    print(scrape_all())