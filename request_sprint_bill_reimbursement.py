from seleniumwire import webdriver
from sprint_scraper import parse_bill, calculate_amounts_due
from paypal_requester import request_payments

import datetime


# Create a new instance of the Chrome driver
driver = webdriver.Chrome('/usr/local/bin/chromedriver')


# Navigate to Sprint, log in, and get bill detail
response = parse_bill(driver)


# Parse bill detail to determine amounts due for each payee
final_amounts_due = calculate_amounts_due(driver, response)


# Prepare memo to accompany paypal request
startDate = response["bill_period_from"]
endDate = response["bill_period_to"]
billMonth = datetime.datetime.strptime(startDate, "%Y-%m-%d").date().strftime("%B")
memo = f"{billMonth} sprint bill for period ending {endDate}"

print(f"\n\n\n FINAL TALLY FOR {billMonth.upper()}: {final_amounts_due}\n\n\n")


# Navigate to Paypal, log in, and request amounts for each payee
request_payments(driver, final_amounts_due, memo)


driver.quit()
