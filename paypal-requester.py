from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# credentials stored locally and .gitignore-d
import secrets
import time

# Create a new instance of the Chrome driver
driver = webdriver.Chrome('/usr/local/bin/chromedriver')


"""
	STEP 1: LOG INTO PAYPAL AND NAVIGATE TO MONEY REQUESTS PAGE
"""

# go to Request Money on paypal, which will redirect to a login page
driver.get("https://www.paypal.com/myaccount/transfer/homepage/request")

# wait for login page to load
WebDriverWait(driver, 60).until(EC.presence_of_element_located((
	By.ID, "email")))

print(driver.title, '\n')

# find the form inputs and submit button element
usernameInput = driver.find_element(By.ID, "email")
passwordInput = driver.find_element(By.ID, "password")
nextButton = driver.find_element(By.ID, "btnNext")
submitButton = driver.find_element(By.ID, "btnLogin")

# log in with credentials, with some time in between actions to simulate user limitations
usernameInput.send_keys(secrets.PAYPAL_USERNAME)
time.sleep(2)

if nextButton:
	nextButton.click()

# wait just in case we had to click the next button to render the password input and submit button
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((
	By.ID, "btnLogin")))

passwordInput.send_keys(secrets.PAYPAL_PASSWORD)
time.sleep(2)

# submit the form
submitButton.click()

print(driver.title, '\n')

# TO DO: sometimes paypal gets hung up on the captcha and redirects to a "try again" page
#				 this may have been fixed by adding the waits (time.sleep())s between actions
#				 if it happens again, add code path to automatically retry login in the above scenario

# wait for money requests page to load
WebDriverWait(driver, 60).until(EC.presence_of_element_located((
	By.ID, "fn-requestRecipient")))

print(driver.title, '\n')

# input box for payee - NB: autocomplete/ typeahead
payeeInput = driver.find_element(By.ID, "fn-requestRecipient")
for person in secrets.EMAILS:
	payeeInput.send_keys(person.email)
	payeeInput.send_keys(Keys.RETURN)

# next button only enabled when valid email entered
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((
	By.CSS_SELECTOR, "span.recipient-next > button")))

nextButton = driver.find_element(By.CSS_SELECTOR, "span.recipient-next > button")
nextButton.click()

# wait for request preview page to load
WebDriverWait(driver, 60).until(EC.presence_of_element_located((
	By.ID, "fn-amount")))


# TO DO: request actual amounts from each person
# 			 maybe add everyone on previous page, and then use split bill feature?
#				 will have to total amount due (except me) and input that at the top
#				 then edit each amount manually

