from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup
import oracledb
import numpy as np
import pandas as pd

v_process_user = 'U1'

if (v_process_user == 'U1'):    start_sno = 1;  end_sno = 500 
elif (v_process_user == 'U2'):  start_sno = 501;   end_sno = 1000
elif (v_process_user == 'U3'):  start_sno = 1001;  end_sno = 1500
elif (v_process_user == 'U4'):  start_sno = 1501;    end_sno = 2000
elif (v_process_user == 'U5'):  start_sno = 2001;    end_sno = 2500
elif (v_process_user == 'U6'):  start_sno = 2501;    end_sno = 3000
elif (v_process_user == 'D1'):  start_sno = 3001;   end_sno = 3500
elif (v_process_user == 'D2'):  start_sno = 3501;   end_sno = 4000
elif (v_process_user == 'D3'):  start_sno = 4001;   end_sno = 4500
elif (v_process_user == 'D4'):  start_sno = 4501;   end_sno = 5000  
elif (v_process_user == 'D5'):  start_sno = 5001;   end_sno = 5500
elif (v_process_user == 'D6'):  start_sno = 5501;   end_sno = 6000 
elif (v_process_user == 'S1'):  start_sno = 6001;   end_sno = 6500 
elif (v_process_user == 'S2'):  start_sno = 6501;   end_sno = 7000
elif (v_process_user == 'S3'):  start_sno = 7001;  end_sno = 7500
elif (v_process_user == 'S4'):  start_sno = 7501;    end_sno = 8000
elif (v_process_user == 'S5'):  start_sno = 8001;    end_sno = 8500
elif (v_process_user == 'S6'):  start_sno = 8501;    end_sno = 9000
elif (v_process_user == 'C1'):  start_sno = 9001;   end_sno = 9500
elif (v_process_user == 'C2'):  start_sno = 9501;   end_sno = 10000
elif (v_process_user == 'C3'):  start_sno = 10001;   end_sno = 10500
elif (v_process_user == 'C4'):  start_sno = 10501;   end_sno = 11000  
elif (v_process_user == 'C5'):  start_sno = 11001;   end_sno = 11500
elif (v_process_user == 'C6'):  start_sno = 11501;   end_sno = 15000

driver = webdriver.Chrome()
driver_qa = webdriver.Chrome()
driver_qa1 = webdriver.Chrome()

oracledb.init_oracle_client(lib_dir=r"D:\app\udaykumard\product\instantclient_23_6")
conn = oracledb.connect(user='RESULT', password='LOCALDEV', dsn='192.168.15.208:1521/orcldev')
cur = conn.cursor()

str_Jeeappno = \
"SELECT SNO, REGNO, TRIM(DOB), MOBILE1 FROM I_JEEADV_ADMITCARD_25 WHERE DOB IS NOT NULL AND TRIM(PROCESS_STATUS_URL) = 'P' \
ORDER BY SNO"

cur.execute(str_Jeeappno)
res = cur.fetchall()

for row in res:
    v_SNO = row[0]
    v_REGNO = row[1]
    v_dob = row[2]
    v_day = v_dob[0:2]
    v_month = v_dob[3:5]
    v_year = v_dob[6:10]
    v_MOBILE = row[3]

    try:
        driver = webdriver.Chrome()
        driver.maximize_window()

        driver.get("https://results.jeeadv.ac.in/")
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

        invalid_login = driver.find_element(By.XPATH, "/html/body/div[1]").text
        if invalid_login !='There is an error in the information entered. Please try again or contact organizing institute (Email: orgjee@iitm.ac.in)':
            View_Responses = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/ul/li[3]/a/span'))
            ).click()

            Error_msg = driver.find_element(By.XPATH, '//*[@id="main-container"]/div[2]/div/div[2]/div[3]/div/div[2]/div/h3').text
            if Error_msg != 'You were absent in Paper 1 and/or Paper 2 of JEE (Advanced) 2025\nHence the responses are not available':
                href_link = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div[3]/div/div[2]/div/table/tbody/tr[1]/td[2]/a")
                url_link = href_link.get_attribute("href")

                driver_qa = webdriver.Chrome()
                driver_qa.maximize_window()
                driver_qa.get(url_link)

                payload = {}
                headers = {}

                response = requests.request("POST", url_link, headers=headers, data=payload)
                soup = BeautifulSoup(response.text, 'html.parser')
                div_text = soup.find("div", {"class": "main-info-pnl"})
                table_data = div_text.find('table').find_all('tr')

                data = []
                for row in table_data:
                    row_data = []
                    for cell in row.find_all('td'):
                        row_data.append(cell.text)
                    data.append(row_data)

                o_ParticipantID = data[0][1]
                o_ParticipantName = data[1][1]
                o_TestCenterName = data[2][1]
                o_TestDate = data[3][1]
                o_TestTime = data[4][1]
                o_Subject = data[5][1]
            
                try:
                    #---------PAPER 1 - DATAFRAME DECLARATION
                    df_paper1 = pd.DataFrame(columns=('PARTICIPANTID', 'QNO', 'QUESTION_TYPE', 'QUESTION_ID', 'OPTION_1_ID', 'OPTION_2_ID', 'OPTION_3_ID', 'OPTION_4_ID', 
                                            'CHOSEN_OPTION', 'SECTION'))
                    
                    #---------PAPER 2 - DATAFRAME DECLARATION
                    df_paper2 = pd.DataFrame(columns=('PARTICIPANTID', 'QNO', 'QUESTION_TYPE', 'QUESTION_ID', 'OPTION_1_ID', 'OPTION_2_ID', 'OPTION_3_ID', 'OPTION_4_ID', 
                                            'CHOSEN_OPTION', 'SECTION'))

                    def append_row(df, row):
                        return pd.concat([
                                        df, 
                                        pd.DataFrame([row], columns=row.index)
                                        ]).reset_index(drop=True)
                    
                    #region "----- START OF PAPER 1 (Questions and Answers)---------------------------------------------""
                    div_questions = soup.find_all("div", {"class": "grp-cntnr"})

                    for div in div_questions:
                        questions_data = div.find_all("div", {"class": "section-cntnr"})
                        for section in questions_data:
                            o_section_name = section.find("span", {"class": "bold"}).text.strip()  # Section name
                            question_v = section.find_all('tr')
                            q_data = []
                            for question in question_v:
                                row_qs = []
                                for cell in question.find_all('td'):
                                    row_qs.append(cell.text)
                                q_data.append(row_qs)
                            
                            for q in q_data:
                                if len(q) >= 18:  # For MCQ and MSQ type questions
                                    o_QuestionNo = q[1]
                                    o_QuestionType = q[13]
                                    o_QuestionID = q[15]
                                    o_ChosenOption = q[17]
                                    # print(o_QuestionNo, o_QuestionType, o_QuestionID, o_ChosenOption, o_section_name)

                                    new_row = pd.Series({'PARTICIPANTID': o_ParticipantID,'QNO':o_QuestionNo,'QUESTION_TYPE': o_QuestionType,'QUESTION_ID': o_QuestionID,'OPTION_1_ID': '','OPTION_2_ID': '',
                                                    'OPTION_3_ID': '','OPTION_4_ID': '','CHOSEN_OPTION': o_ChosenOption,'SECTION':o_section_name})
                                        
                                    df_paper1 = append_row(df_paper1, new_row)

                                    

                                elif len(q) >= 11 and q[8].strip() == 'SA':  # For SA type questions
                                    o_QuestionNo = q[1]
                                    o_QuestionType = q[8]
                                    o_QuestionID = q[10]
                                    o_GivenAnswer = q[6]
                                    # print(o_QuestionNo, o_QuestionType, o_QuestionID, o_ChosenOption, o_section_name)

                                    new_row = pd.Series({'PARTICIPANTID': o_ParticipantID,'QNO':o_QuestionNo,'QUESTION_TYPE': o_QuestionType,'QUESTION_ID': o_QuestionID,'OPTION_1_ID': '','OPTION_2_ID': '',
                                                    'OPTION_3_ID': '','OPTION_4_ID': '','CHOSEN_OPTION': o_GivenAnswer,'SECTION':o_section_name})
                                        
                                    df_paper1 = append_row(df_paper1, new_row)

                        qalist_paper_1 = []
                        qalist_paper_1 = df_paper1.values.tolist()
                        #df_paper1.to_excel("paper1.xlsx")

                        #-----------START OF INSERTION OF STUDENT DETAILS---------------------------------------------------------------------
                        insert_stu_dtls = \
                            "INSERT INTO OUT_JEE_ADVANCED_2025 (PARTICIPANTID, PARTICIPANTNAME, TESTCENTER, TESTDATE, TESTTIME, SUBJECT, SUBJECT1,  PROCESS_STATUS, PROCESS_USER, \
                        CREATEDDATE, ERROR_MESSAGE, SNO, REGNO) \
                            VALUES ('"+ o_ParticipantID +"', '"+ o_ParticipantName +"','"+ o_TestCenterName +"', '"+ o_TestDate +"', '"+ o_TestTime +"', '"+ o_Subject +"', \
                            '', 'DONE', '"+ v_process_user +"', SYSDATE, '', '"+str(v_SNO)+"', '"+v_REGNO+"')"
                    
                        print(insert_stu_dtls)
                                                
                        cur.execute(insert_stu_dtls) # Execute an INSERT statement
                        #-----------END OF INSERTION OF STUDENT DETAILS---------------------------------------------------------------------

                        #-----------START OF INSERTION OF STUDENT QUESTION AND ANSWER DETAILS -  PAPER 1---------------------------------------------------------------------
                        cur.setinputsizes(None, 20)
                        insert_qa_paper1 = """insert into OUT_JEE_ADVANCED_2025_QA1 (PARTICIPANTID, QNO, QUESTION_TYPE, QUESTION_ID, OPTION_1_ID, OPTION_2_ID, OPTION_3_ID, OPTION_4_ID, 
                        CHOSEN_OPTION, SECTION)
                                values (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10 )"""
                        cur.executemany(insert_qa_paper1, qalist_paper_1)

                        
                        #-----------END OF INSERTION OF STUDENT QUESTION AND ANSWER DETAILS - PAPER 1---------------------------------------------------------------------    


                        #-----------START OF UPDATE OF INPUT TABLE-------------------------------------------------------------------------------------------------------
                        update_IpStatus = "UPDATE IN_ADV_RESPONSES_2025 SET PROCESS_STATUS_PAPER1 = 'D', PROCESS_USER = '"+v_process_user+"' WHERE REGNO = '"+ str(v_REGNO) +"'"
                        cur.execute(update_IpStatus) # Execute an UPDATE statement
                        conn.commit()
                        #-----------END OF UPDATE OF INPUT TABLE---------------------------------------------------------------------------------------------------------

                        #endregion "----- END OF PAPER 1 (Questions and Answers) --------------------------------------------------------------------------------------------------------"
                
                    #region "----- START OF PAPER 2 (Questions and Answers)---------------------------------------------""
                    href_link1 = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div[3]/div/div[2]/div/table/tbody/tr[2]/td[2]/a")
                    url_link1 = href_link1.get_attribute("href")

                    driver_qa1 = webdriver.Chrome()
                    driver_qa1.maximize_window()
                    driver_qa1.get(url_link1)

                    payload = {}
                    headers = {}

                    response = requests.request("POST", url_link1, headers=headers, data=payload)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    div_text = soup.find("div", {"class": "main-info-pnl"})
                    table_data1 = div_text.find('table').find_all('tr')

                    data = []
                    for row in table_data1:
                        row_data = []
                        for cell in row.find_all('td'):
                            row_data.append(cell.text)
                        data.append(row_data)

                    ParticipantID1 = data[0][1]
                    Subject1 = data[5][1]

                    update_stu_dtls = "UPDATE OUT_JEE_ADVANCED_2025 SET SUBJECT1 = '"+ Subject1 +"' WHERE PARTICIPANTID = '"+ ParticipantID1 +"'"
                    cur.execute(update_stu_dtls) # Execute an INSERT statement

                    div_questions = soup.find_all("div", {"class": "grp-cntnr"})

                    for div in div_questions:
                        questions_data = div.find_all("div", {"class": "section-cntnr"})
                        for section in questions_data:
                            o_section_name_2 = section.find("span", {"class": "bold"}).text.strip()  # Section name
                            question_v = section.find_all('tr')
                            q_data = []
                            for question in question_v:
                                row_qs = []
                                for cell in question.find_all('td'):
                                    row_qs.append(cell.text)
                                q_data.append(row_qs)
                            
                            for q in q_data:
                                if len(q) >= 18:  # For MCQ and MSQ type questions
                                    o_QuestionNo_2 = q[1]
                                    o_QuestionType_2 = q[13]
                                    o_QuestionID_2 = q[15]
                                    o_ChosenOption_2 = q[17]
                                    # print(o_QuestionNo_2, o_QuestionType_2, o_QuestionID_2, o_ChosenOption_2, o_section_name_2)

                                    new_row = pd.Series({'PARTICIPANTID': o_ParticipantID,'QNO':o_QuestionNo_2,'QUESTION_TYPE': o_QuestionType_2,'QUESTION_ID': o_QuestionID_2,'OPTION_1_ID': '','OPTION_2_ID': '',
                                                    'OPTION_3_ID': '','OPTION_4_ID': '','CHOSEN_OPTION': o_ChosenOption_2,'SECTION':o_section_name_2})
                                        
                                    df_paper2 = append_row(df_paper2, new_row)

                                    

                                elif len(q) >= 11 and q[8].strip() == 'SA':  # For SA type questions
                                    o_QuestionNo_2 = q[1]
                                    o_QuestionType_2 = q[8]
                                    o_QuestionID_2 = q[10]
                                    o_GivenAnswer_2 = q[6]
                                    # print(o_QuestionNo_2, o_QuestionType_2, o_QuestionID_2, o_ChosenOption_2, o_section_name_2)

                                    new_row = pd.Series({'PARTICIPANTID': o_ParticipantID,'QNO':o_QuestionNo_2,'QUESTION_TYPE': o_QuestionType_2,'QUESTION_ID': o_QuestionID_2,
                                                        'OPTION_1_ID': '','OPTION_2_ID': '', 'OPTION_3_ID': '','OPTION_4_ID': '','CHOSEN_OPTION': o_GivenAnswer_2,
                                                        'SECTION':o_section_name_2})
                                        
                                    df_paper2= append_row(df_paper2, new_row)

                        qalist_paper_2 = []
                        qalist_paper_2 = df_paper2.values.tolist()
                        #df_paper1.to_excel("paper1.xlsx")

                        #-----------START OF INSERTION OF STUDENT QUESTION AND ANSWER DETAILS -  PAPER 1---------------------------------------------------------------------
                        cur.setinputsizes(None, 20)
                        insert_qa_paper2 = """insert into OUT_JEE_ADVANCED_2025_QA2 (PARTICIPANTID, QNO, QUESTION_TYPE, QUESTION_ID, OPTION_1_ID, OPTION_2_ID, OPTION_3_ID, OPTION_4_ID, 
                        CHOSEN_OPTION, SECTION)
                                values (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10 )"""
                        cur.executemany(insert_qa_paper2, qalist_paper_2)

                        
                        #-----------END OF INSERTION OF STUDENT QUESTION AND ANSWER DETAILS - PAPER 1---------------------------------------------------------------------    


                        #-----------START OF UPDATE OF INPUT TABLE-------------------------------------------------------------------------------------------------------
                        update_IpStatus1 = "UPDATE IN_ADV_RESPONSES_2025 SET PROCESS_STATUS_PAPER2 = 'D', PROCESS_USER = '"+v_process_user+"' WHERE REGNO = '"+ str(v_REGNO) +"'"
                        cur.execute(update_IpStatus1) # Execute an UPDATE statement
                        conn.commit()
                        #-----------END OF UPDATE OF INPUT TABLE---------------------------------------------------------------------------------------------------------

                        #endregion "----- END OF PAPER 1 (Questions and Answers) --------------------------------------------------------------------------------------------------------"
                
                except Exception as e:
                    print(e)
                    pass
                    update_IpStatus1 = "UPDATE IN_ADV_RESPONSES_2025 SET PROCESS_STATUS_PAPER1 = 'P, PROCESS_USER = '"+v_process_user+"' WHERE REGNO = '"+ str(v_REGNO) +"'"
                    cur.execute(update_IpStatus1) # Execute an UPDATE statement
                    conn.commit()
            else:
                update_IpStatus1 = "UPDATE IN_ADV_RESPONSES_2025 SET PROCESS_STATUS_PAPER1 = 'AB', PROCESS_USER = '"+v_process_user+"' WHERE REGNO = '"+ str(v_REGNO) +"'"
                cur.execute(update_IpStatus1) # Execute an UPDATE statement 
                conn.commit() 
        else:
            update_IpStatus1 = "UPDATE IN_ADV_RESPONSES_2025 SET PROCESS_STATUS_PAPER1 = 'NA', PROCESS_USER = '"+v_process_user+"' WHERE REGNO = '"+ str(v_REGNO) +"'"
            cur.execute(update_IpStatus1) # Execute an UPDATE statement  
            conn.commit()
    except:
        update_IpStatus1 = "UPDATE IN_ADV_RESPONSES_2025 SET PROCESS_STATUS_PAPER1 = 'NA', PROCESS_USER = '"+v_process_user+"' WHERE REGNO = '"+ str(v_REGNO) +"'"
        cur.execute(update_IpStatus1) # Execute an UPDATE statement
        conn.commit()
    
    finally:
        driver.quit()
        driver_qa.quit()
        driver_qa1.quit()
