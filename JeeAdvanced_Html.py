import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup
import oracledb

v_process_user = 'U1'
    
if (v_process_user == 'U1'): 
    start_sno = 1;  end_sno = 1000
elif (v_process_user == 'U2'):
    start_sno = 1001;   end_sno = 2000
elif (v_process_user == 'U3'):
    start_sno = 2001;  end_sno = 3000
elif (v_process_user == 'U4'):
    start_sno = 3001;    end_sno = 4000
elif (v_process_user == 'U5'):
    start_sno = 4001;    end_sno = 5000
elif (v_process_user == 'U6'):
    start_sno = 5001;    end_sno = 6000
elif (v_process_user == 'D1'):
    start_sno = 6001;   end_sno = 7000
elif (v_process_user == 'D2'):
    start_sno = 7001;   end_sno = 8000
elif (v_process_user == 'D3'):
    start_sno = 8001;   end_sno = 9000
elif (v_process_user == 'D4'):
    start_sno = 9001;   end_sno = 10000  
elif (v_process_user == 'D5'):
    start_sno = 10001;   end_sno = 11000
elif (v_process_user == 'D6'):
    start_sno = 11001;   end_sno = 13000    

# Setup the folder to save HTML files
save_folder = "jeeadv_responses_paper1"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

save_folder1 = "jeeadv_responses_paper2"
if not os.path.exists(save_folder1):
    os.makedirs(save_folder1)

oracledb.init_oracle_client(lib_dir=r"D:\app\udaykumard\product\instantclient_23_6")
conn = oracledb.connect(user='RESULT', password='LOCALDEV', dsn='192.168.15.208:1521/orcldev')
cur = conn.cursor()

str_Jeeappno = \
    "SELECT SNO, REGNO, TRIM(DOB), MOBILE1 FROM I_JEEADV_ADMITCARD_25  \
        WHERE DOB IS NOT NULL AND TRIM(PROCESS_STATUS_URL) = 'P' AND SNO >= '"+str(start_sno)+"' AND  SNO <='"+str(end_sno)+"' ORDER BY SNO"

cur.execute(str_Jeeappno)
res = cur.fetchall()

for row in res:
    driver = webdriver.Chrome()
    driver.maximize_window()

    v_SNO = row[0]
    v_REGNO = row[1]
    v_dob = row[2]
    v_day = v_dob[0:2]
    v_month = v_dob[3:5]
    v_year = v_dob[6:10]
    v_MOBILE = row[3]

    try:
        driver.get("https://cportal7.jeeadv.ac.in/")
        time.sleep(1)

        Mobile_number = driver.find_element(By.NAME, "mobileNo")
        Mobile_number.clear()
        Mobile_number.send_keys(v_MOBILE)

        dob = driver.find_element(By.NAME, "datepicker")
        dob.send_keys(v_dob)

        Registration_number = driver.find_element(By.NAME, "AdvAppNo")
        Registration_number.send_keys(v_REGNO)

        time.sleep(0.5)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'login'))
        ).click()

        View_Responses = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/ul/li[3]/a/span'))
        ).click()

        href_link = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div[3]/div/div[2]/div/table/tbody/tr[1]/td[2]/a")
        url_link = href_link.get_attribute("href")

        driver_qa = webdriver.Chrome()
        driver_qa.maximize_window()
        driver_qa.get(url_link)

        payload = {}
        headers = {}

        response = requests.request("POST", url_link, headers=headers, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')

        file_path = os.path.join(save_folder, f"{v_REGNO}.html")
        with open(file_path, "w") as htmlfile:
            htmlfile.write(str(soup))

        href_link1 = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div[3]/div/div[2]/div/table/tbody/tr[2]/td[2]/a")
        url_link1 = href_link1.get_attribute("href")

        driver_qa1 = webdriver.Chrome()
        driver_qa1.maximize_window()
        driver_qa1.get(url_link1)

        payload = {}
        headers = {}

        response = requests.request("POST", url_link1, headers=headers, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        file_path1 = os.path.join(save_folder1, f"{v_REGNO}.html")
        with open(file_path1, "w") as htmlfile:
            htmlfile.write(str(soup))

        insert_jeeadv_url = \
                "INSERT INTO URL_JEEADV_OUTPUT_2025 (REGNO, URL_1, URL_2) \
                VALUES ('"+ str(v_REGNO) +"', '"+ url_link +"','"+ url_link1 +"')"
                
        cur.execute(insert_jeeadv_url) # Execute an INSERT statement

        update_IpStatus = "UPDATE IN_ADV_RESPONSES_2024 SET PROCESS_STATUS_URL = 'D' WHERE REGNO = '"+ str(v_REGNO) +"'"
        cur.execute(update_IpStatus) # Execute an UPDATE statement
        conn.commit()

    except Exception as e:
        update_IpStatus = "UPDATE IN_ADV_RESPONSES_2024 SET PROCESS_STATUS_URL = 'NA' WHERE REGNO = '"+ str(v_REGNO) +"'"
        cur.execute(update_IpStatus) # Execute an UPDATE statement
        conn.commit()

driver.quit()
driver_qa.quit()
driver_qa1.quit()