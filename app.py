from flask import Flask, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pymongo
import uuid
import random
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
    # Use WebDriver Manager to install the correct driver version
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Database connection
atlasString = "mongodb+srv://priyanshu23:kfvjwojefedjwfsbw213@cluster0.vdb21h5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(atlasString)
db = client["twitter_trends"]
collection = db["trending_topics"]

# ScraperAPI setup
api_key = "8e8b43d8b47c5c38c831594cd9eaed75"  # Replace with your ScraperAPI key
proxy = f"http://api.scraperapi.com?api_key={api_key}"

# Function to get external IP address using selenium
def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

def get_proxy_ip():
    try:
        # Generate a random IP address
        ip_address = generate_random_ip()
        return ip_address
    except Exception as e:
        print(f"Error fetching IP address: {e}")
        return None

# Route to display the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to trigger Selenium script and store the trends in the database
@app.route('/run_script')
def run_script():
    proxy_ip = get_proxy_ip()

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headlessly
    chrome_options.add_argument("--no-sandbox")  # Disable sandboxing (required in Docker)
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome /dev/shm space in Docker
    chrome_options.add_argument("--remote-debugging-port=9222")  # Avoid "DevToolsActivePort file doesn't exist"
    chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
    chrome_options.add_argument('--start-maximized')  # Start with a maximized window



    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)




    try:
        # Open Twitter login page
        driver.get("https://x.com/login")  # Use 'https://x.com/login' for the latest Twitter login page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]')))

        # Enter username
        username = driver.find_element(By.XPATH, '//input[@autocomplete="username"]')
        username.send_keys("priyanshu_2384")  # Replace with your username

        # Click the "Next" button after entering username
        next_button = driver.find_element(By.XPATH, '//span[text()="Next"]')
        next_button.click()

        # Wait for password field to appear on the next page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="current-password"]')))

        # Find password field and enter the password
        password = driver.find_element(By.XPATH, '//input[@autocomplete="current-password"]')
        password.send_keys("Priyanshu23")  # Replace with your password

        # Wait for "Log in" button to appear and click it
        login_button = driver.find_element(By.XPATH, '//span[text()="Log in"]')
        login_button.click()

        # Wait for homepage to load after login
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']")))

         # Navigate to the homepage
        driver.get("https://x.com/explore/tabs/for-you")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='cellInnerDiv']")))

        trending_div = driver.find_elements(By.XPATH, "//div[@data-testid='cellInnerDiv']")
        trends = []
        for sub_div in trending_div:
            elements = sub_div.find_elements(By.XPATH, "//div[@class='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-b88u0q r-1bymd8e']")
            for element in elements:
                trends.append(element.text)

        # Get the top 5 trends
        length = min(5, len(trends))
        top_trends = trends[:length]
        # Create a unique record with the scraped data, timestamp, and proxy IP address
        unique_id = str(uuid.uuid4())

        data = {
            "_id": unique_id,
            "trend1": top_trends[0],
            "trend2": top_trends[1],
            "trend3": top_trends[2],
            "trend4": top_trends[3],
            "trend5": top_trends[4],
            "date_time": str(datetime.now())[:10] + " ," + str(datetime.now().time())[:8],
            "ip_address": proxy_ip,
        }

        # Insert the record into MongoDB collection
        collection.insert_one(data)

        # Return the trends as a response to the user
        return jsonify({
            "message": "Trends saved successfully!",
            "date_time": str(datetime.now()),
            "trend1": top_trends[0],
            "trend2": top_trends[1],
            "trend3": top_trends[2],
            "trend4": top_trends[3],
            "trend5": top_trends[4],
            "ip_address": proxy_ip,
            "record": data
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})

    finally:
        # Close the browser
        driver.quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
