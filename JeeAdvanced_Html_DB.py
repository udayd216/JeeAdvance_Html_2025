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

oracledb.init_oracle_client(lib_dir=r"D:\app\udaykumard\product\instantclient_23_6")
conn = oracledb.connect(user='RESULT', password='LOCALDEV', dsn='192.168.15.208:1521/orcldev')
cur = conn.cursor()

#--------------------Data slots --------------------------------------
str_dataslot = "SELECT PROCESS_USER, START_VAL, END_VAL FROM DATASLOTS_VAL_USER WHERE PROCESS_USER = '"+v_process_user+"'"
cur.execute(str_dataslot)
res_dataslot = cur.fetchall()

start_sno = res_dataslot[0][1]
end_sno = res_dataslot[0][2]

Sno = start_sno
#------------------------------ end --------------------------------------

str_Jeeappno = \
    "SELECT SNO, REGNO, TRIM(DOB), MOBILE1 FROM I_JEEADV_ADMITCARD_25  \
        WHERE DOB IS NOT NULL AND TRIM(PROCESS_STATUS_URL) = 'P' AND SNO >= '"+str(start_sno)+"' AND  SNO <='"+str(end_sno)+"' ORDER BY SNO"
cur.execute(str_Jeeappno)
res = cur.fetchall()

driver = webdriver.Chrome()
driver.maximize_window()

for row in res:
    v_SNO = row[0]
    v_REGNO = row[1]
    v_dob = row[2].replace("-","/")
    v_MOBILE = row[3]

    try:
        driver.get("https://cportal5.jeeadv.ac.in/")
        time.sleep(1)

        Registration_number = driver.find_element(By.NAME, "regno")
        Registration_number.send_keys(v_REGNO)

        dob = driver.find_element(By.NAME, "dob")
        dob.send_keys(v_dob)

        time.sleep(0.5)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div/form/button'))
        ).click()
        try:
            err_msg = driver.find_element(By.XPATH, "/html/body/p[1]").text
        except:
            err_msg = ''
        if err_msg == 'Invalid Registration Number or Date of Birth.':
            update_IpStatus = "UPDATE I_JEEADV_ADMITCARD_25 SET PROCESS_STATUS_URL = 'INVALID' WHERE REGNO = '"+ str(v_REGNO) +"'"
            cur.execute(update_IpStatus) # Execute an UPDATE statement
            conn.commit()
            
        else:
            href_link = driver.find_element(By.XPATH, "/html/body/div/div/p[1]/a")
            url_link = href_link.get_attribute("href")

            href_link1 = driver.find_element(By.XPATH, "/html/body/div/div/p[2]/a")
            url_link1 = href_link1.get_attribute("href")

            insert_jeeadv_url = \
                    "INSERT INTO URL_JEEADV_OUTPUT_2025 (REGNO, URL_1, URL_2) \
                    VALUES ('"+ str(v_REGNO) +"', '"+ url_link +"','"+ url_link1 +"')"
                    
            cur.execute(insert_jeeadv_url) # Execute an INSERT statement

            update_IpStatus = "UPDATE I_JEEADV_ADMITCARD_25 SET PROCESS_STATUS_URL = 'DONE' WHERE REGNO = '"+ str(v_REGNO) +"'"
            cur.execute(update_IpStatus) # Execute an UPDATE statement
            conn.commit()

    except Exception as e:
        update_IpStatus = "UPDATE I_JEEADV_ADMITCARD_25 SET PROCESS_STATUS_URL = 'NA' WHERE REGNO = '"+ str(v_REGNO) +"'"
        cur.execute(update_IpStatus) # Execute an UPDATE statement
        conn.commit()

driver.quit()
conn.close()