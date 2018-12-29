from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from twilio.rest import Client
from dotenv import load_dotenv
import os
import time

load_dotenv()
print('Loaded dotenv')

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1920x1080')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-extensions')
driver = webdriver.Chrome(chrome_options=chrome_options)
print('Driver started')
driver.get('https://bansso.vcu.edu/ssomanager/c/SSB')

# Log in
print('Logging in...')
username_input = driver.find_element_by_name('username')
password_input = driver.find_element_by_name('password')
username_input.send_keys(os.getenv('VCU_USERNAME'))
password_input.send_keys(os.getenv('VCU_PASSWORD'))
password_input.send_keys(Keys.RETURN)

# Select semester
print('Selecting semester...')
driver.get('https://ssb.vcu.edu/proddad/bwskfcls.p_sel_crse_search')
term_select = Select(driver.find_element_by_name('p_term'))
term_select.select_by_value('201920')
submit_button = driver.find_element_by_xpath('/html/body/div[4]/form/input[2]')
submit_button.click()

# Making advanced search for Chemistry courses
print('Making advanced Chemistry search...')
advanced_search_button = driver.find_element_by_xpath('/html/body/div[4]/form/input[18]')
advanced_search_button.click()
subject_select = Select(driver.find_element_by_xpath('//*[@id="subj_id"]'))
subject_select.select_by_value('CHEM')
submit_button = driver.find_element_by_name('SUB_BTN')
submit_button.click()

notification_sent = False

while notification_sent is False:
    print('Parsing table data...')
    # Parse table data
    table = driver.find_element_by_xpath('/html/body/div[4]/form/table/tbody')
    rows = table.find_elements_by_tag_name('tr')
    target_rows = []

    for row in rows:
        cells = row.find_elements_by_tag_name('td')
        add_row = False

        if len(cells) > 0:
            status = cells[0]
            number = cells[3].text
            section = cells[4].text

            if number == '301':
                if section == '001' or section == '901' or section == '902':
                    add_row = True
            elif number == '303':
                add_row = True
            elif number == '309' and section == '002':
                add_row = True

            if add_row == True:
                target_rows.append([status, number, section])

    # Check target rows for status
    for row in target_rows:
        status_cell = row[0]
        course = 'CHEM ' + row[1] + '-' + row[2]

        if len(status_cell.find_elements_by_tag_name('abbr')) > 0:
            print(course + ' is still closed.')
        else:
            print(course + ' is open! Sending text message...') 
            # Send Twilio text
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
            body_text = course + ' is open!'
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                to='+17037256302', 
                from_='+15402534519',
                body=body_text)
            notification_sent = True
    
    if notification_sent is False:
        # Wait one minute before trying again
        time.sleep(60)
        print('Reloading page...')
        driver.refresh()

driver.close()