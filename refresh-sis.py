from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from twilio.rest import Client
from dotenv import load_dotenv
import os
import time

load_dotenv()

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get("https://ps-sis-sa90.vccs.edu/psp/ps/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_CART.GBL?PORTALPARAM_PTCNAV=HC_SSR_SSENRL_CART_GBL&EOPP.SCNode=HRMS&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=CO_EMPLOYEE_SELF_SERVICE&EOPP.SCLabel=Enrollment&EOPP.SCFName=HCCC_ENROLLMENT&EOPP.SCSecondary=true&EOPP.SCPTfname=HCCC_ENROLLMENT&FolderPath=PORTAL_ROOT_OBJECT.CO_EMPLOYEE_SELF_SERVICE.HCCC_ENROLLMENT.HC_SSR_SSENRL_CART_GBL&IsFolder=false")
driver.implicitly_wait(10)

# Log in
user_field = driver.find_element_by_name("username1")
password_field = driver.find_element_by_name("password")
submit_button = driver.find_element_by_id("submitButton")
user_field.send_keys(os.getenv("VCCS_USERNAME"))
password_field.send_keys(os.getenv("VCCS_PASSWORD"))
submit_button.click()

# Get semester button so the driver waits for it
driver.find_element_by_name('TargetContent')

course_closed = True

while course_closed is True:
    print("Refreshing...")
    driver.refresh()

    # Switch to iframe
    driver.switch_to_default_content()
    driver.switch_to_frame("TargetContent")

    # Select semester
    driver.find_element_by_xpath('//*[@id="SSR_DUMMY_RECV1$sels$1$$0"]').click()
    continue_button = driver.find_element_by_name("DERIVED_SSS_SCT_SSR_PB_GO")
    continue_button.click()
    
    # Switch to new iframe
    driver.switch_to_default_content()
    driver.switch_to_frame("TargetContent")

    # Check status
    status_icon = driver.find_element_by_xpath('//*[@id="win0divDERIVED_REGFRM1_SSR_STATUS_LONG$0"]/div/img')
    status = status_icon.get_attribute('alt')
    if status != 'Closed':
        print("\n\n!!!!!!!The course is open!!!!!!!")
        driver.close()

        # Send Twilio text
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token  = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            to="+17037273862", 
            from_="+18045543991",
            body="CSC 202 is open!")

        course_closed = False
    else:
        print('The course was closed')
        time.sleep(60)