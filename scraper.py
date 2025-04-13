from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment if you don't need to see the browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_shl_catalog():
    url = "https://www.shl.com/solutions/products/product-catalog/?start=12&type=1&type=1"
    driver = setup_driver()
    driver.get(url)
    
    # Wait for the page to load
    time.sleep(5)
    
    all_assessment_links = []
    current_page = 2
    total_pages = 32  # As specified
    
    try:
        # Accept cookies if present
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            time.sleep(2)
        except:
            print("No cookie dialog found or already accepted")
        
        while current_page <= total_pages:
            print(f"Scraping page {current_page} of {total_pages}")
            
            # Specifically find the second table with the combined classes
            # This will target the div that has both classes
            table_wrapper = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.custom__table-wrapper.js-target-table-wrapper"))
            )
            
            # Find the responsive table inside this wrapper
            table_responsive = table_wrapper.find_element(By.CLASS_NAME, "custom__table-responsive")
            
            # Find all links within the responsive table
            assessment_elements = table_responsive.find_elements(By.TAG_NAME, "a")
            
            print(f"Found {len(assessment_elements)} links on page {current_page}")
            
            # Extract links and titles
            for element in assessment_elements:
                try:
                    link = element.get_attribute('href')
                    title = element.text.strip()
                    
                    if link and title and link not in [item['url'] for item in all_assessment_links]:
                        all_assessment_links.append({
                            'title': title,
                            'url': link
                        })
                        print(f"Found assessment: {title} ({link})")
                except Exception as e:
                    print(f"Error extracting link: {e}")
            
            # Go to next page if not on the last page
            if current_page < total_pages:
                try:
                    # Find the pagination within the second table wrapper
                    pagination = table_wrapper.find_element(By.CLASS_NAME, "pagination")
                    
                    # Click the "Next" button
                    next_button = pagination.find_element(By.CSS_SELECTOR, ".pagination__item--arrow-next")
                    driver.execute_script("arguments[0].scrollIntoView();", next_button)
                    driver.execute_script("arguments[0].click();", next_button)
                    
                    # Wait for the next page to load
                    time.sleep(3)
                    current_page += 1
                except Exception as e:
                    print(f"Error navigating to next page: {e}")
                    # Try an alternative method
                    try:
                        # Try using XPath with the specific section context
                        next_button = driver.find_element(By.XPATH, "//div[contains(@class, 'custom__table-wrapper') and contains(@class, 'js-target-table-wrapper')]//a[text()='Next']")
                        driver.execute_script("arguments[0].scrollIntoView();", next_button)
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(3)
                        current_page += 1
                    except:
                        print("Both methods to find Next button failed. Trying direct URL navigation.")
                        # Try direct URL navigation as last resort
                        driver.get(f"https://www.shl.com/solutions/products/product-catalog/?start={(current_page)*8}&type=1&type=1")
                        time.sleep(5)
                        current_page += 1
            else:
                break
                
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        
    # Save the links to a file
    with open('shl_assessment_links.json', 'w') as f:
        json.dump(all_assessment_links, f, indent=2)
        
    print(f"Scraping completed. Found {len(all_assessment_links)} unique assessment links.")
    return all_assessment_links

if __name__ == "__main__":
    assessment_links = scrape_shl_catalog()
    print(f"Total assessment links collected: {len(assessment_links)}")