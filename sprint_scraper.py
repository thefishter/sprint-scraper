from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import secrets			# credentials stored locally and .gitignore-d
import json


def parse_bill(driver):
	"""
		STEP 1: LOG INTO SPRINT AND NAVIGATE TO VIEW MY BILL
	"""

	# go to my bill on sprint, which will redirect to a login page
	driver.get("https://www.sprint.com/en/my-sprint/view-my-bill.html")

	print(driver.title, '\n')

	# wait for page to load
	WebDriverWait(driver, 60).until(EC.presence_of_element_located((
		By.ID, "loginHeaderUsername")))

	# find the form inputs and submit button element
	# stupidly on sprint's side, they do not follow the convention that IDs must be unique, so we need to find both/ all and select the one we need
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

	# TO DO: add code path for 2FA possibility


	"""
		STEP 2: INTERCEPT XHR REQUEST TO GET BILL DETAIL
	"""

	# wait for the bill detail XHR request on the View My Bill page to complete
	billDetailRequest = driver.wait_for_request("/api/digital/V21-a/documents/8176664570-0477019317_145_201910_21?ban=477019317", timeout=60)
	# TO DO: use string interpolation to fix date in URL
	#				 also test to see nothing else changes month to month

	# reformat JSON response (bytes object) to stringified JSON to python dict
	response = json.loads(billDetailRequest.response.body.decode("utf-8"))
	return response


def calculate_amounts_due(driver, response):
	"""
		STEP 3: PARSE BILL DETAIL FOR RELEVANT COSTS
	"""
	accountsDetail = response["assets"]
	globalBillItems = response["global_bill_items"]
	taxes = float(response["total_tax"]["amount"])
	surcharges = 0

	# tally and split all shared costs evenly
	for item in globalBillItems:
		surcharges += float(item["bill_item_summary"]["amount_ex_tax"])

	print(f"\n\n Surcharges: {surcharges}")
	print(f"\n Taxes: {taxes}")
	print(f"\n TOTAL SHARED COSTS: {taxes + surcharges}")


	"""
		STEP 4: FINALIZE AMOUNTS DUE PER PERSON
	"""

	# aggregate all non shared costs per person
	accountTotals = {}
	for account in accountsDetail:
		# if placeholder account for plan subscription, move onto the next account
		reference = int(account["reference"])
		if (reference == 0):
			continue
		# collect basic info
		name = account["subscriber_name"].split()[0].lower() # get first name only
		number = account["phone_number"]
		account_total = 0
		# sum up bill items per account
		for bill_item in account["bill_items_group"]:
			account_total += float(bill_item["bill_item_summary"]["amount_ex_tax"])
		# add to dict
		if name not in accountTotals.keys():
			accountTotals[name] = account_total
		else:
			accountTotals[name] += account_total

	print(f"\n\n\n Aggregated Account Totals: {accountTotals}")

	# add 5-way split of shared costs to each amount due
	split = round((taxes + surcharges) / secrets.NUM_ACCOUNTS, 2)
	final_amounts_due = [accountTotals[person["name"]] + split for person in secrets.PAYEES]
	# account for one person paying for two shares each month
	final_amounts_due[-1] += (accountTotals[secrets.PRIMARY] + split)

	return final_amounts_due
