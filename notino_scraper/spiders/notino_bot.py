import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from scrapy.selector import Selector
import time

class NotinoBotSpider(scrapy.Spider):
    name = "notino_bot"
    start_urls = ["https://www.notino.pl/perfumy-kobiety/"]

    def parse(self, response):
        self.logger.info(">>> ODPALAMY HYBRYDĘ (FIREFOX + SCRAPY) <<<")
        
        options = Options()
        # options.add_argument('-headless') 
        
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        
        try:
            driver.get(response.url)
            time.sleep(5) 
            
            sel = Selector(text=driver.page_source)
            # Używamy selektora z Twojego HTMLa
            produkty = sel.css('div[data-testid="product-container"]')
            
            self.logger.info(f"!!! Znalazłem {len(produkty)} produktów !!!")
            
            for p in produkty:
                yield {
                    "marka": p.css('h2[data-testid="product-tile-brand"]::text').get(),
                    "nazwa": p.css('h3[data-testid="product-tile-name"]::text').get(),
                    "cena": p.css('span[data-testid="price-component"]::text').get(),
                    "ocena": p.css('span[data-testid="product-ratings-num"]::text').get(),
                    "liczba_opinii": p.css('span[data-testid="product-ratings-numReview"]::text').get(),
                    "link": "https://www.notino.pl" + p.css('a::attr(href)').get()
                }
                
        finally:
            driver.quit()