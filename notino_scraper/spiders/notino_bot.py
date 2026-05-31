import scrapy
# MAGIA: Importujemy niewykrywalnego Chrome'a
import undetected_chromedriver as uc
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

class NotinoBotSpider(scrapy.Spider):
    name = "notino_bot"
    start_urls = ["https://www.notino.pl/perfumy-kobiety/"]
    handle_httpstatus_list = [403, 301, 302]

    def parse(self, response):
        self.logger.info(">>> ODPALAMY BOTA (UNDETECTED CHROME - OMIJANIE CLOUDFLARE) <<<")
        
        # Konfiguracja Niewykrywalnego Chrome'a
        options = uc.ChromeOptions()
        # options.add_argument('--headless') # Kiedy zadziała, możesz to odkomentować
        
        # Odpalamy ukrytą przeglądarkę
        driver = uc.Chrome(options=options, version_main=148)        
        try:
            numer_strony = 1
            
            while True:
                if numer_strony == 1:
                    url = response.url
                else:
                    # Twój sprawdzony i idealnie działający link!
                    url = f"https://www.notino.pl/perfumy-kobiety/?f={numer_strony}-1-55544-55545"
                
                self.logger.info(f">>> Wczytuję STRONĘ {numer_strony} ({url}) <<<")
                driver.get(url)
                
                try:
                    # Czekamy na kafelki z perfumami
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="product-container"]'))
                    )
                except Exception as e:
                    self.logger.info(f"!!! Koniec czasu lub brak perfum na stronie {numer_strony}. Kończę scraper.")
                    break 
                    
                time.sleep(2) # Dajemy 2 sekundy na wyrenderowanie tekstów i cen
                
                sel = Selector(text=driver.page_source)
                produkty = sel.css('div[data-testid="product-container"]')
                
                if len(produkty) == 0:
                    break
                    
                self.logger.info(f"!!! SSAM DANE: Znalazłem {len(produkty)} produktów na stronie {numer_strony} !!!")
                
                for p in produkty:
                    raw_opinii = p.xpath('.//span[@data-testid="product-ratings-numReview"]//text()').getall()
                    czysta_liczba_opinii = "".join(raw_opinii).replace("(", "").replace(")", "").strip()

                    yield {
                        "marka": p.css('h2[data-testid="product-tile-brand"]::text').get(),
                        "nazwa": p.css('h3[data-testid="product-tile-name"]::text').get(),
                        "cena": p.css('span[data-testid="price-component"]::text').get(),
                        "ocena": p.css('span[data-testid="product-ratings-num"]::text').get(),
                        "liczba_opinii": czysta_liczba_opinii,
                        "link": "https://www.notino.pl" + p.css('a::attr(href)').get()
                    }
                
                numer_strony += 1
                
        finally:
            self.logger.info(">>> Zescrapowano. Zamykam przeglądarkę. <<<")
            driver.quit()