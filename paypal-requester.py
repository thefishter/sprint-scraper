from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# credentials stored locally and .gitignore-d
import secrets
import time

# # Create a new instance of the Chrome driver
# driver = webdriver.Chrome('/usr/local/bin/chromedriver')

def request_payments(driver, amounts_due, memo):
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


	"""
		STEP 2: ENTER ALL PAYEES TO INITIATE SIMULTANEOUS REQUEST
	"""

	# wait for money requests page to load
	WebDriverWait(driver, 60).until(EC.presence_of_element_located((
		By.ID, "fn-requestRecipient")))

	print(driver.title, '\n')

	# add all payees to input box - NB: has autocomplete/ typeahead functionality
	payeeInput = driver.find_element(By.ID, "fn-requestRecipient")
	for person in secrets.PAYEES:
		payeeInput.send_keys(person["email"])
		time.sleep(1)
		payeeInput.send_keys(Keys.RETURN)
		time.sleep(2)

	# next button only enabled when valid email(s) entered
	WebDriverWait(driver, 60).until(EC.element_to_be_clickable((
		By.CSS_SELECTOR, "span.recipient-next > button")))

	nextButton = driver.find_element(By.CSS_SELECTOR, "span.recipient-next > button")
	nextButton.click()


	"""
		STEP 3: SUBMIT TO EACH PAYEE FOR RESPECTIVE AMOUNTS CALCULATED FROM BILL
	"""

	# wait for request preview page to load
	WebDriverWait(driver, 60).until(EC.presence_of_element_located((
		By.ID, "fn-amount")))

	totalInput = driver.find_element(By.ID, "fn-amount")
	splitButton = driver.find_element(By.ID, "split-request")

	# sum up total amount to request from everyone, cast to string to be inputted
	total = str(sum(amounts_due))
	totalInput.send_keys(total)

	# paypal automatically assumes that you want each person to pay you this amount
	#	solution: change mode from Request Money to Split Bill
	splitButton.click()

	# paypal assumes next that you want this total to be equally split amongst payees
	# solution: wait til UI changes and then manually edit each amount due
	WebDriverWait(driver, 60).until(EC.presence_of_element_located((
		By.ID, "split-request-tab")))

	actions = ActionChains(driver)
	actions.send_keys(Keys.TAB)

	numPayees = len(amounts_due)

	for i in range(numPayees):
		print(amounts_due[i])
		actions.send_keys(Keys.TAB) \
					 .send_keys(Keys.BACK_SPACE * 6) \
					 .send_keys(str(amounts_due[i])) \
					 .pause(1)

	# add memo for requests
	actions.send_keys(Keys.TAB * 2)
	actions.send_keys(memo)

	actions.pause(2)

	# submit requests
	actions.send_keys(Keys.TAB)
	actions.send_keys(Keys.RETURN)

	actions.perform()

	# TO DO: check for success response
