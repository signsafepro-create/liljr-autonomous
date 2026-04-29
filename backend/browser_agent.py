"""
BROWSER AUTOMATION MODULE
Control websites, scrape data, login, interact
Uses requests + BeautifulSoup + Selenium if available
"""
import requests
import json
import time
import os
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except:
    BS4_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
except:
    SELENIUM_AVAILABLE = False

class BrowserAgent:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"
        })
        self.driver = None
        self.cookies: Dict[str, str] = {}
        self.history: List[str] = []
    
    def _init_selenium(self) -> bool:
        """Initialize headless browser if available"""
        if not SELENIUM_AVAILABLE:
            return False
        try:
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 14)")
            self.driver = webdriver.Chrome(options=options)
            return True
        except:
            return False
    
    def fetch_page(self, url: str) -> Dict:
        """Fetch and parse webpage"""
        try:
            resp = self.session.get(url, timeout=15)
            self.history.append(url)
            result = {
                "status": resp.status_code,
                "url": url,
                "title": "",
                "links": [],
                "forms": [],
                "text": ""
            }
            if BS4_AVAILABLE:
                soup = BeautifulSoup(resp.text, "html.parser")
                title = soup.find("title")
                result["title"] = title.text if title else ""
                result["links"] = [{"text": a.text.strip(), "href": a.get("href", "")} 
                                    for a in soup.find_all("a") if a.get("href")][:50]
                result["forms"] = self._parse_forms(soup)
                # Remove script/style for clean text
                for tag in soup(["script", "style"]):
                    tag.decompose()
                result["text"] = soup.get_text(separator="\n", strip=True)[:5000]
            else:
                result["text"] = resp.text[:5000]
            return result
        except Exception as e:
            return {"status": "error", "message": str(e), "url": url}
    
    def _parse_forms(self, soup) -> List[Dict]:
        """Parse all forms on page"""
        forms = []
        for form in soup.find_all("form"):
            fields = []
            for input_tag in form.find_all(["input", "textarea", "select"]):
                fields.append({
                    "name": input_tag.get("name", ""),
                    "type": input_tag.get("type", "text"),
                    "id": input_tag.get("id", ""),
                    "placeholder": input_tag.get("placeholder", "")
                })
            forms.append({
                "action": form.get("action", ""),
                "method": form.get("method", "get").upper(),
                "fields": fields
            })
        return forms
    
    def submit_form(self, url: str, data: Dict, method: str = "POST") -> Dict:
        """Submit form data"""
        try:
            if method.upper() == "POST":
                resp = self.session.post(url, data=data, timeout=15)
            else:
                resp = self.session.get(url, params=data, timeout=15)
            return {"status": resp.status_code, "url": resp.url, "response": resp.text[:2000]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def login(self, url: str, username: str, password: str, 
              user_field: str = "username", pass_field: str = "password") -> Dict:
        """Login to website"""
        try:
            # First get the page to extract form
            page = self.fetch_page(url)
            if page.get("status") != 200:
                return {"status": "error", "message": "Could not load login page"}
            
            # Submit login
            data = {user_field: username, pass_field: password}
            result = self.submit_form(url, data, "POST")
            
            # Check if login succeeded (look for redirects, cookies, etc)
            if result["status"] in [200, 302]:
                return {"status": "success", "message": "Login submitted", "cookies": dict(self.session.cookies)}
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scrape_element(self, url: str, selector: str, by: str = "css") -> Dict:
        """Scrape specific element"""
        try:
            if SELENIUM_AVAILABLE and not self.driver:
                self._init_selenium()
            
            if self.driver:
                self.driver.get(url)
                time.sleep(2)
                if by == "css":
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                elif by == "xpath":
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.ID, selector)
                
                results = []
                for el in elements[:20]:
                    results.append({
                        "text": el.text,
                        "href": el.get_attribute("href") or "",
                        "src": el.get_attribute("src") or "",
                        "html": el.get_attribute("outerHTML")[:500]
                    })
                return {"status": "ok", "count": len(results), "data": results}
            else:
                # Fallback to requests + bs4
                page = self.fetch_page(url)
                if BS4_AVAILABLE and page.get("status") == 200:
                    soup = BeautifulSoup(page["text"], "html.parser")
                    if by == "css":
                        elements = soup.select(selector)
                    else:
                        elements = soup.find_all(attrs={"id": selector})
                    return {"status": "ok", "count": len(elements), "data": [el.text[:200] for el in elements[:20]]}
                return {"status": "error", "message": "Selenium not available and bs4 failed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def click_element(self, url: str, selector: str) -> Dict:
        """Click element via Selenium"""
        if not SELENIUM_AVAILABLE:
            return {"status": "error", "message": "Selenium not installed"}
        try:
            if not self.driver:
                self._init_selenium()
            self.driver.get(url)
            time.sleep(2)
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
            time.sleep(1)
            return {"status": "clicked", "new_url": self.driver.current_url}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def type_in_field(self, url: str, selector: str, text: str, submit: bool = False) -> Dict:
        """Type text into field"""
        if not SELENIUM_AVAILABLE:
            return {"status": "error", "message": "Selenium not installed"}
        try:
            if not self.driver:
                self._init_selenium()
            self.driver.get(url)
            time.sleep(2)
            field = self.driver.find_element(By.CSS_SELECTOR, selector)
            field.clear()
            field.send_keys(text)
            if submit:
                field.send_keys(Keys.RETURN)
            return {"status": "typed", "text": text[:50]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None

browser = BrowserAgent()
