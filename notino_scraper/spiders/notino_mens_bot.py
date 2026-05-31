import scrapy
import undetected_chromedriver as uc
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

class NotinoMensBotSpider(scrapy.Spider):
    name = "notino_mens_bot"
    
    start_urls = ["https://www.notino.pl/perfumy-mezczyzni/"]
    handle_httpstatus_list = [403, 301, 302]

    def parse(self, response):
        self.logger.info(">>> ODPALAMY BOTA (MĘSKIE PERFUMY) <<<")
        
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, version_main=148) #wersja 148 chrome
        
        try:
            numer_strony = 1
            
            while True:
                if numer_strony == 1:
                    url = response.url
                else:
                    url = f"https://www.notino.pl/perfumy-mezczyzni/?f={numer_strony}-1-55544-55549"
                
                self.logger.info(f">>> Wczytuję STRONĘ {numer_strony} ({url}) <<<")
                driver.get(url)
                
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="product-container"]'))
                    )
                except Exception as e:
                    self.logger.info(f"Brak perfum na stronie {numer_strony}.")
                    break 
                    
                time.sleep(2) 
                
                sel = Selector(text=driver.page_source)
                produkty = sel.css('div[data-testid="product-container"]')
                
                if len(produkty) == 0:
                    break
                    
                self.logger.info(f"Znalazłem {len(produkty)} produktów na stronie {numer_strony}")
                
                for p in produkty:
                    href = p.css('a::attr(href)').get()
                    
                    if not href:
                        continue
                        
                    raw_opinii = p.xpath('.//span[@data-testid="product-ratings-numReview"]//text()').getall()
                    czysta_liczba_opinii = "".join(raw_opinii).replace("(", "").replace(")", "").strip()

                    yield {
                        "marka": p.css('h2[data-testid="product-tile-brand"]::text').get(),
                        "nazwa": p.css('h3[data-testid="product-tile-name"]::text').get(),
                        "cena": p.css('span[data-testid="price-component"]::text').get(),
                        "ocena": p.css('span[data-testid="product-ratings-num"]::text').get(),
                        "liczba_opinii": czysta_liczba_opinii,
                        "link": "https://www.notino.pl" + href
                    }
                
                numer_strony += 1
                
        finally:
            self.logger.info(">>> Zescrapowano. Zamykam przeglądarkę. <<<")
            driver.quit()