import scraper_classes as SC
import scraper_exceptions as SE
from pathlib import Path

if __name__ == '__main__':

    scraper = SC.GoogleScraper(
        keyword='Airline Stocks', 
        search_start_date='06/01/2019', 
        periods=int(365/2),
        save_to_location = Path.cwd(),
        max_header_word_count=20,
        max_text_word_count = 400, 
        periodicity='2D',
        google_results_pages=2,
        headless=True,
        )
    scraper.scrape()