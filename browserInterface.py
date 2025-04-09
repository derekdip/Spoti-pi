from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException , ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import re

# Step 1: Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
chrome_options.add_argument("--no-sandbox")  # Disable sandboxing (useful for running on limited environments like Raspberry Pi)
chrome_options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage (to avoid crashes)

    # Step 2: Set up the service to specify the path of ChromeDriver (chromedriver)
chromedriver_path = '/Users/derekpenaloza/Downloads/chromedriver-mac-arm64/chromedriver'  # Path to chromedriver
service = Service(chromedriver_path)
    # Set up WebDriver (Make sure to replace the path with your local chromedriver path)
driver = webdriver.Chrome(service=service)  # Update this path

def logIn():

    # Open Spotify web player
    driver.get("https://accounts.spotify.com/en/login?login_hint=1derek2penaloza3%40gmail.com&allow_password=1")

    # Allow some time for the page to load
    sleep(5)



    #class="e-9800-baseline e-9800-overflow-wrap-anywhere e-9800-button-primary__inner encore-inverted-light-set e-9800-button--medium"
    # Example: Search for a song by name (You can modify this part to play anything you want)


    password_input = driver.find_element(By.XPATH, "//input[@data-testid='login-password']")
    password_input.click()
    password_input.send_keys("qwer1234")  # Replace with your actual password


    login_button = driver.find_element(By.XPATH, "//button[@data-testid='login-button']")
    login_button.click()

    sleep(2)
    # Find the "Web Player" button using its data-testid attribute and click it
    web_player_button = driver.find_element(By.XPATH, "//button[@data-testid='web-player-link']")
    web_player_button.click()



    sleep(2) 

def parseInput(name:str):
    result= name.lower()
    result = re.sub(r'[^a-z0-9\n ]', '', result)
    result = re.sub(r'\s+', ' ', result)
    result = result.replace(' ', '%20')
    return result

def search(name):
    #https://open.spotify.com/search/no%20where%20to%20go
    query =parseInput(name)
    print(query)
    driver.get("https://open.spotify.com/search/"+query)
    sleep(2)
    web_player_button = driver.find_element(By.XPATH, "//div[@data-testid='herocard-click-handler']")
    web_player_button.click()
    sleep(2)
    try:
        # Locate the button using XPath
        # hover_element = driver.find_elements(By.XPATH, '//button[@data-testid="play-button" and @aria-label="Play"]')
        # actions = ActionChains(driver)
        # actions.move_to_element(hover_element).perform()  # Hover over the element
        # sleep(1)
        elements = driver.find_elements(By.CLASS_NAME, 'e-9800-button-primary')
        for element in elements:
            print(element)
        elements[2].click()
    except ElementNotInteractableException as e:
        print(f'Error: Element is not interactable - {str(e)}')
    except NoSuchElementException as e:
        print(f'Error: {str(e)}')  # Print the error message if the button is not found
    except Exception as e:  # Catch all exceptions as a variable e
        print(f"Error Type: {type(e)}")  # Print the type of the exception
        print(f"Error Message: {str(e)}")  # Print the message of the exception
    return None

def endSession():
    driver.quit()