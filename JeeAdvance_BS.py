import oracledb
import requests
import urllib3
from bs4 import BeautifulSoup
from pdf2image import convert_from_bytes
import pytesseract
import cv2
import numpy as np

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Step 1: Start a session
session = requests.Session()

v_process_user = 'U1'

# Step 2: Define URLs
login_url = "https://cportal5.jeeadv.ac.in/authenticate.php"
result_url = "https://cportal5.jeeadv.ac.in/dashboard.php"

oracledb.init_oracle_client(lib_dir=r"D:\app\udaykumard\product\instantclient_23_6")
conn = oracledb.connect(user='RESULT', password='LOCALDEV', dsn='192.168.15.208:1521/orcldev')
cur = conn.cursor()

#---------------Data Slots--------------------------------
str_dataslot = "SELECT PROCESS_USER, START_VAL, END_VAL FROM DATASLOTS_VAL_USER WHERE PROCESS_USER = '"+v_process_user+"'"
cur.execute(str_dataslot)
res_dataslot = cur.fetchall()

start_sno = res_dataslot[0][1]
end_sno = res_dataslot[0][2]

Sno = start_sno
#---------------------------------- End ---------------------------

#str_Jeeappno = "SELECT SNO, REGNO, DOB, MOBILENO, MOBILE1, MOBILE2, ADMNO FROM I_JEEADV_ADMITCARD_25 WHERE REGNO ='K41421092663'"
str_Jeeappno = "SELECT SNO, REGNO, DOB, MOBILENO, MOBILE1, MOBILE2, ADMNO FROM I_JEEADV_ADMITCARD_25 WHERE PROCESS_STATUS_URL = 'DONE' \
AND SNO >= '"+str(start_sno)+"' AND  SNO <='"+str(end_sno)+"' ORDER BY SNO"
cur.execute(str_Jeeappno)
res = cur.fetchall()

for row in res:
    v_appno = row[1]     
    v_password = row[2].replace("-","/")
    v_mobile = row[3]
    v_mobile1 = row[4]
    v_mobile2 = row[5]
    v_admno = row[6]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://cportal5.jeeadv.ac.in/",
    }

    # Step 3: GET the login page
    response = session.get(login_url, headers=headers, verify=False)
    response.raise_for_status()

    # Step 4: Parse hidden fields (if needed in the future)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Step 5: Fill login form data
    data = {
        "regno" : "K42421033751",
        "dob" : "20/03/2007",
        "login": ""
    }

    try:
        # Step 6: POST login form
        post_response = session.post(login_url, headers=headers, data=data, verify=False, allow_redirects=False)

        if post_response.status_code in [302, 301]:
            location = post_response.headers.get('Location', result_url)
            if not location.startswith('http'):
                location = result_url

            result_response = session.get(location, headers=headers, verify=False)
            result_response.raise_for_status()

            # Extract all hrefs from <a> tags that contain "Download Responses"
            links = []
            for a_tag in result_response.find_all('a', class_='btn btn-success'):
                href = a_tag.get('href')
                if href:
                    # Make absolute URL if necessary
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = 'https://your_base_url_here' + href
                    links.append(href)

            with open("document.pdf", "wb") as f:
                f.write(result_response.content)

            import fitz  # PyMuPDF

            with fitz.open("document.pdf") as doc:
                html_output = ""
                for page in doc:
                    html_output += page.get_text("html")

            print(html_output)  # This is the HTML-like structure representing the PDF layout


        elif post_response.status_code in[200, 500]:
            update_IpStatus = "UPDATE I_JEEADV_ADMITCARD_25 SET PROCESS_STATUS = 'NA' WHERE REGNO = '"+ str(v_appno) +"'"
            cur.execute(update_IpStatus) # Execute an UPDATE statement
            conn.commit()
    except:
        update_IpStatus = "UPDATE I_JEEADV_ADMITCARD_25 SET PROCESS_STATUS = 'NA' WHERE REGNO = '"+ str(v_appno) +"'"
        cur.execute(update_IpStatus) # Execute an UPDATE statement
        conn.commit()