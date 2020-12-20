import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from dateutil.relativedelta import relativedelta
import time
from typing import List
from abc import ABC, abstractproperty, abstractmethod

import scraper_exceptions as SE



class ArticlePage(dict):
    def __init__(self, title, headers, text, date, link, max_header_word_count=20, max_text_word_count=400, **kwargs):
        super().__init__(title=title, headers=self.truncate_text(headers, max_header_word_count), text=self.truncate_text(text, max_text_word_count),date=date,link=link, **kwargs) 
    @staticmethod
    def truncate_text(string: str, max_words: int) -> str:
        last_word_index = -1
        spaces_count = 0
        for i in range(len(string)):
            if string[i] == ' ':
                spaces_count += 1
            if spaces_count == max_words:
                last_word_index = i
                return string[:last_word_index]
        return string
    @property
    def word_count(self):
        return self['text'].count(' ')+1






class BaseScraper:
    
    def __init__(self, headless=True):
        self.headless = headless
        self._browser = self._open_new_browser()
        
    @property
    def browser(self):
        return self._browser
            
            
    @SE.ExceptionHandler(SE.BrowserStartException, True)
    def _open_new_browser(self):
        options = ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        options.add_experimental_option("prefs",prefs)
        if self.headless == True:
            options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--use-gl=desktop')
        options.add_argument('--log-level=3')
        options.add_argument("--disable-extensions")
        options.add_argument("--incognito")
        
        browser = Chrome(executable_path=ChromeDriverManager().install(), options=options)
        return browser
    
        
    @SE.ExceptionHandler(SE.BrowseToPageException, raise_error=True)
    def _browse_to_page(self, url):   
        self.browser.get(url)
        
    # The following methods were created to be used instead of the
    # original simple Selenium methods that search for elements immediately without
    # giving the browser time to finish loading the elements.
    
    # by xpath
    @SE.ExceptionHandler(SE.GetElementException, raise_error=True)    
    def _get_element_by_xpath(self, xpath, wait_sec=5):
        return (WebDriverWait(self.browser, wait_sec)
            .until(EC.presence_of_all_elements_located((By.XPATH, xpath)))[0])
    
    @SE.ExceptionHandler(SE.GetElementException, raise_error=True)    
    def _get_elements_by_xpath(self, xpath, wait_sec=5):
        return (WebDriverWait(self.browser, wait_sec)
            .until(EC.presence_of_all_elements_located((By.XPATH, xpath))))
    
    
    # by class name
    @SE.ExceptionHandler(SE.GetElementException, raise_error=True)        
    def _get_element_by_class_name(self, class_name, wait_sec=5):
        return (WebDriverWait(self.browser, wait_sec)
            .until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))[0])
    
    @SE.ExceptionHandler(SE.GetElementException, raise_error=True)                    
    def _get_elements_by_class_name(self, class_name, wait_sec=5):
        return (WebDriverWait(self.browser, wait_sec)
            .until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))))
       
       
    # by css selector
    @SE.ExceptionHandler(SE.GetElementException, raise_error=True)                              
    def _get_element_by_css_selector(self, css_selector, wait_sec=5):
        return (WebDriverWait(self.browser, wait_sec)
            .until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))[0])

    @SE.ExceptionHandler(SE.GetElementException, raise_error=True)                              
    def _get_elements_by_css_selector(self, css_selector, wait_sec=5):
        return (WebDriverWait(self.browser, wait_sec)
            .until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))))


    # by tag name
    @SE.ExceptionHandler(SE.GetElementException, raise_error=True)                                  
    def _get_element_by_tag_name(self, tag_name, wait_sec=5):
        return (WebDriverWait(self.browser, wait_sec)
            .until(EC.presence_of_all_elements_located((By.TAG_NAME, tag_name)))[0])

    @SE.ExceptionHandler(SE.GetElementException, raise_error=True)                                  
    def _get_elements_by_tag_name(self, tag_name, wait_sec=5):
        return (WebDriverWait(self.browser, wait_sec)
            .until(EC.presence_of_all_elements_located((By.TAG_NAME, tag_name))))


    # by id
    @SE.ExceptionHandler(SE.GetElementException, raise_error=True)         
    def _get_element_by_id(self, id, wait_sec=5):
        return (WebDriverWait(self.browser, wait_sec)
            .until(EC.presence_of_all_elements_located((By.ID, id))))[0]   
    











class GoogleScraper(BaseScraper):
    
    def __init__(self, keyword, search_start_date, periods, save_to_location, browser_wait_time = 5, max_header_word_count=20, max_text_word_count=400, periodicity='M', google_results_pages=5, **kwargs):
        super().__init__(**kwargs)
        self.keyword = keyword
        self.save_to_location = save_to_location
        self.browser_wait_time = browser_wait_time
        self.max_header_word_count = max_header_word_count
        self.max_text_word_count = max_text_word_count
        self.google_results_pages = google_results_pages
        self.search_periods = self.generate_date_ranges(search_start_date, periods, periodicity)
        self.articles_scraped_counter = 0

    @SE.ExceptionHandler(SE.BrowserStartException, raise_error=True)
    def _change_google_to_english(self):
        lang_panel = self._get_element_by_id('SIvCob')
        lang_panel.find_element_by_xpath("//*[contains(text(), 'English')]").click()
          
          
    @SE.ExceptionHandler(SE.InfoCollectionException, raise_error=False)
    def _collect_p_tags(self):
        paragraphs = self._get_elements_by_css_selector('p', self.browser_wait_time)
        return ' '.join([para.text for para in paragraphs])


    @SE.ExceptionHandler(SE.InfoCollectionException, raise_error=False)
    def _collect_h_tags(self):
        header_elements = self._get_elements_by_css_selector("h1, h2, h3, h4, h5, h6", self.browser_wait_time)
        return '. '.join([header.text for header in header_elements])


    @SE.ExceptionHandler(SE.InfoCollectionException, raise_error=False)     
    def _collect_title(self):
        return (self._get_element_by_xpath('/html/head/title', self.browser_wait_time)
                    .get_attribute('textContent')
                    .strip())

    
    @staticmethod
    @SE.ExceptionHandler(SE.DateRangeGenerationException, raise_error=True)
    def generate_date_ranges(start_date, periods, periodicity):
        """Generate two lists with period start and end dates.

        Args:
            start_date (str): Google search period starting date string.
            periods (int): Number of periods to scrape. (e.g. scraping 10 periods, 3 days each will scrape data ranging 30 days)
            periodicity (str): Length of periods (e.g. '4D' will search periods spanning 4 days each)

        Raises:
            ValueError: 'periodicity' cannot be shorter than daily.

        Returns:
            tuple(list[datetime], list[datetime]): Tuple containing two lists of datetime objects. First contains the period start dates, the second one contains period end dates. Used in setting time periods in Google Search Tools.
        """
        if periodicity in ['BH','H','T','min','S','L','ms','us','U','N']:
            raise ValueError('Scraper does not support periodicities shorter than daily.')
        if periodicity in ['D','B']:
            from_dates = pd.date_range(start_date, periods=periods, freq=periodicity)
            to_dates = from_dates.copy()
        else:
            if periods==1:
                from_dates = pd.date_range(start_date, periods=2, freq=periodicity)
                to_dates = pd.date_range(from_dates[1]+relativedelta(days=-1), periods=2, freq=periodicity)
                return [(from_dates[0], to_dates[0])]
            else:
                from_dates = pd.date_range(start_date, periods=periods, freq=periodicity)
                to_dates = pd.date_range(from_dates[1]+relativedelta(days=-1), periods=periods, freq=periodicity)
                return list(zip(from_dates, to_dates))



    @SE.ExceptionHandler(SE.DateRangeGenerationException, raise_error=True)
    def _set_custom_date_period(self, from_date, to_date, current_period):
        """Set a custom search period in Google Search.

        Args:
            from_date (str): (format MM/DD/YYYY) Start of period.
            to_date (str): (format MM/DD/YYYY) End of period.
        """
        
        # Wait for appearance of "Tools" panel (it is clicked elsewhere during the first time page is opened; does not need to be clicked again during all subsequent scrapings)      
        time.sleep(0.5)
        xpath = '//div[@class="hdtb-mn-cont"]'
        self._get_element_by_xpath(xpath, self.browser_wait_time)
        
        # click "Time" button
        time.sleep(0.5)
        xpath = '//div[@class="mn-hd-txt"]'
        self._get_element_by_xpath(xpath, self.browser_wait_time).click() 
        
        # click "Custom Range" button
        time.sleep(0.5)
        xpath = '//span[@role="menuitem" and @jsaction="EEGHee" and @tabindex="-1"]'
        self._get_element_by_xpath(xpath, self.browser_wait_time).click()            
        
        # enter "from" date into search tools
        time.sleep(0.5)
        from_path = "//*[@id='OouJcb']"
        from_field = self._get_element_by_xpath(from_path, self.browser_wait_time)
        try: from_field.clear().send_keys(from_date)
        except: from_field.send_keys(from_date)
        
        # enter "to" date into search tools
        time.sleep(0.5)
        to_path = "//*[@id='rzG2be']"
        to_field = self._get_element_by_xpath(to_path, self.browser_wait_time)
        try: to_field.clear().send_keys(to_date)
        except: to_field.send_keys(to_date)
        
        # click "Go" button
        time.sleep(0.5)
        go_path = '//g-button[@class="Ru1Ao BwGU8e fE5Rge"]'
        self._get_element_by_xpath(go_path, self.browser_wait_time).click()


    @staticmethod
    @SE.ExceptionHandler(SE.DateLinkCollectionException, raise_error=False)
    def _collect_date_link_from_element(element):
        href = element.find_element_by_tag_name('a').get_attribute('href')
        date = (element.find_element_by_class_name("f")
                    .get_attribute('textContent')
                    .split('—')[0]
                    .strip())
        return href, date
        
        
    @SE.ExceptionHandler(SE.DateLinkCollectionException, raise_error=True)
    def _collect_dates_links(self, xpaths_to_try):
        for xpath in xpaths_to_try:
            try:
                page_results = self._get_elements_by_xpath(xpath)
                if page_results:
                    print('page_results: ', len(page_results))
                    break
            except: pass
        dates = []
        links = []
        for result in page_results:
            try:
                link, date = self._collect_date_link_from_element(result)
                links.append(link)
                dates.append(date)
            except: pass
        return dates, links


    @SE.ExceptionHandler(SE.ResultsPageCollectionException, raise_error=True)
    def _collect_search_results_article_data(self):
        main_tab = self.browser.window_handles[0] # save the handle of the main search tab

        xpaths_to_try = ["//div[@id='rso']/div[@class='g']/div[@class='rc']", 
                         "//div[@class='hlcw0c']/div[@class='g']/div[@class='rc']", 
                         "//div[@class='g']/span/div[@class='rc']",
                         ]
        dates, links = self._collect_dates_links(xpaths_to_try)
        results_page = []
    
        for date, link in zip(dates, links):
            self.browser.execute_script(f"window.open('{link}', 'new window')") # open link in a new tab
            self.browser.switch_to.window(window_name=self.browser.window_handles[1]) # switch Selenium to the new tab

            print('\ndate: ', date)
            print('link: ', link)
            
            try: title = self._collect_title()
            except: title = ''
            if title == None:
                title = ''
            print('Title word count: ', title.count(' ')+1)
            
            try: headers = self._collect_h_tags()
            except: headers = ''
            if headers == None:
                headers = ''
            print('Headers original word count: ', headers.count(' ')+1 if len(headers)>0 else 0)
            
            try: text = self._collect_p_tags()
            except: text = ''
            if text == None:
                text = ''
            print('Text original word count: ', text.count(' ')+1 if len(text)>0 else 0)

            article = ArticlePage(title = title, 
                                  headers = headers, 
                                  text = text, 
                                  link = link, 
                                  date = date,
                                  max_header_word_count = self.max_header_word_count,
                                  max_text_word_count = self.max_text_word_count,
                                  ) 
            
            self.articles_scraped_counter+=1
            print('Articles scraped: ', self.articles_scraped_counter)

            self.browser.close() # close the article tab
            self.browser.switch_to.window(window_name=main_tab) # return to main search tab

            results_page.append(article)
        return results_page


    @SE.ExceptionHandler(SE.ClickException, raise_error=True)
    def _next_google_results_page(self, page_no):
        """Open a specific google search page in search results window.

        Args:
            page_no (int): Number of search results page to open.
        """
        self.browser.switch_to.window(window_name=self.browser.window_handles[0])
        self._get_element_by_xpath(f'//a[@aria-label="Page {page_no}"]').click()



    def scrape(self):
        """Scrape Google Search for text on entered keyword and for set date period. Saves files to specified location.
        """
        self._browse_to_page('https://www.google.com/')
        self._change_google_to_english()
        self._get_element_by_xpath('//input[@type="text"]').send_keys(self.keyword) #enter keyword
        time.sleep(0.5)
        self._get_element_by_xpath("//input[@type='submit']").click() #submit keyword for search
        
        # loop through date periods
        current_period = 1
        for from_d, to_d in self.search_periods:
            period_contents = []
            from_d = from_d.strftime('%m/%d/%Y')
            to_d = to_d.strftime('%m/%d/%Y')
            # ensure the current results page is not larger than variable "google_results_pages"
            current_page = 1
            while current_page <= self.google_results_pages:
                print(f'\n\ncurrent_period: {current_period}; total_periods: {len(self.search_periods)}')
                print(f'current_page: {current_page}; google_results_pages: {self.google_results_pages}')
                if current_page == 1:
                    if current_period == 1:
                        xpath = '//div[@id="hdtb-tls"]'
                        self._get_element_by_xpath(xpath).click() # clicking Tools button, stays active during subsequent results pages so no need to repeat step
                    self._set_custom_date_period(from_d, to_d, current_period)
                    content = self._collect_search_results_article_data()
                    period_contents.extend(content)
                    current_page += 1

                elif current_page > 1:
                    try:
                        self._next_google_results_page(str(current_page))
                        content = self._collect_search_results_article_data()
                        period_contents.extend(content)
                        current_page += 1
                    except:
                        current_page = self.google_results_pages+1
            current_period +=1

            period_contents_df = pd.DataFrame({
                'title': list(map(lambda x: x['title'], period_contents)),
                'headers': list(map(lambda x: x['headers'], period_contents)),
                'text': list(map(lambda x: x['text'], period_contents)),
                'date': list(map(lambda x: x['date'], period_contents)),
                'link': list(map(lambda x: x['link'], period_contents)),
            })
            columns = ['title','headers','text','date','link']
            period_contents_df = period_contents_df.reindex(columns=columns)

            save_to = f'{self.save_to_location}\\{from_d}_to_{to_d}_{self.keyword}.csv'.replace('/', '-').replace(' ', '_')
            period_contents_df.to_csv(save_to)
