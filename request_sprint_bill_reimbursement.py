from seleniumwire import webdriver
from sprint_scraper import parse_bill, calculate_amounts_due
from paypal_requester import request_payments

from datetime import date, datetime
import sys
import secrets

# Create a new instance of the Chrome driver
driver = webdriver.Chrome('/usr/local/bin/chromedriver')


# Navigate to Sprint, log in, and get bill detail for current month
today = date.today()

if today.day < 21:
	lastIssueDate = date(today.year, today.month - 1, 21)

month = int(sys.argv[1]) if len(sys.argv) > 1 else lastIssueDate.month
year = int(sys.argv[2]) if len(sys.argv) > 2 else lastIssueDate.year

billIssueDate = date(year, month, 21)
diffInMonths = (billIssueDate.year - secrets.START_BILL_ISSUE_DATE.year) * 12 + billIssueDate.month - secrets.START_BILL_ISSUE_DATE.month

billIssueNumber = secrets.START_BILL_ISSUE_NUMBER + diffInMonths

print(f"RETRIEVING BILL #{billIssueNumber} FOR {month}/{year}\n\n")
response = parse_bill(driver, year, month, billIssueNumber)


# Parse bill detail to determine amounts due for each payee
final_amounts_due = calculate_amounts_due(driver, response)


# Prepare memo to accompany paypal request
startDate = response["bill_period_from"]
endDate = response["bill_period_to"]
billMonth = datetime.strptime(endDate, "%Y-%m-%d").date().strftime("%B")
memo = f"{billMonth} sprint bill for period ending {endDate}"

print(f"\n\n\n FINAL TALLY FOR {billMonth.upper()}: {final_amounts_due}\n\n\n")


# Navigate to Paypal, log in, and request amounts for each payee
request_payments(driver, final_amounts_due, memo)


driver.quit()
