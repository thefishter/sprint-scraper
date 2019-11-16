from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# credentials stored locally and .gitignore-d
import secrets

# Create a new instance of the Chrome driver
driver = webdriver.Chrome('/usr/local/bin/chromedriver')

# go to my bill on sprint, which will redirect to a login page
driver.get("https://www.sprint.com/en/my-sprint/view-my-bill.html")

print(driver.title, '\n')

# wait for page to load
WebDriverWait(driver, 60)
	.until(EC.presence_of_element_located((By.ID, "loginHeaderUsername")))

# find the form inputs and submit button element
# stupidly on sprint's side, they do not follow the convention that IDs must be unique,
# so we need to find both/ all and select the one we need
possibleInputs = driver.find_elements(By.ID, "loginHeaderUsername")
usernameInput = possibleInputs[1]

possiblePwInputs = driver.find_elements(By.ID, "loginHeaderPassword")
passwordInput = possiblePwInputs[1]

possibleSubmitButtons = driver.find_elements(By.ID, "loginHeaderButton")
submitButton = possibleSubmitButtons[1]

# log in with credentials - first, click to focus element
usernameInput.click()
usernameInput.send_keys(secrets.USERNAME)
passwordInput.click()
passwordInput.send_keys(secrets.PASSWORD)

# submit the form
submitButton.click()

# wait for the page to load
WebDriverWait(driver, 10).until(EC.title_contains("Bill"))
print(driver.title)

# finally:
# 	driver.quit()
