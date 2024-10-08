from config import Config
import imaplib
import logging
import email
from email.message import EmailMessage
from bs4 import BeautifulSoup
import pandas as pd
import fitz
import os
import datetime
import io
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
import ssl 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

conf=Config()

# set up logging to file
logging.basicConfig(
     filename=conf.log_file,
     level=logging.INFO, 
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
 )

class Mail:
    def connect_to_gmail_imap(self, user, password):
        imap_url = 'imap.gmail.com'
        try:
            mail = imaplib.IMAP4_SSL(imap_url)
            mail.login(user, password)
            mail.select('inbox')
            return mail
        except Exception as e:
            print("Connection failed: {}".format(e))
            raise

    def get_mails(self):
        context=ssl.create_default_context()
        mail=self.connect_to_gmail_imap(conf.email_user, conf.email_password)
        self.invoices_dir=f"/Users/wojtekmarszalek/Desktop/Osobiste/Nauka/Python/PythonScripts/Personal/Petrol_Invoices/Invoices/{datetime.datetime.now().month}_Miesiac"
        if os.path.isdir(self.invoices_dir):
            pass
        else:
            os.makedirs(self.invoices_dir, exist_ok=True)
        counter=0
        dfs_list=[]
        result, data=mail.search(None, 'SUBJECT "Potwierdzenie transakcji Shell SmartPay"')
        if result=="OK":
            for num in data[0].split():
                counter+=1
                result, data= mail.fetch(num, "(RFC822)")
                if result == "OK":
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    date_recieved=datetime.datetime.strptime((msg["Date"][5:16]).strip(), "%d %b %Y")
                    if date_recieved.month>=datetime.datetime.now().month-1 and date_recieved.year==datetime.datetime.now().year and msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            try:
                                body = part.get_payload(decode=True).decode()
                                attachment = msg.get_payload()[1]
                                attachment_name=attachment.get_filename()
                                attachment_name=attachment_name[:attachment_name.find(".")]
                                open(f'{self.invoices_dir}/{attachment_name}_{counter}.pdf', 'wb').write(attachment.get_payload(decode=True))
                            except:
                                pass   
                            if content_type == "text/html":
                                soup=BeautifulSoup(body, 'html.parser')
                                table=soup.find("table")
                                if table:
                                    table=str(table)
                                    table=io.StringIO(table)
                                    df=pd.read_html(table, flavor="html5lib")[0]
                                    price=df.iloc[17,1]
                                    transact=df.iloc[6,1]
                                    data=[[date_recieved, price, transact]]
                                    prices_df=pd.DataFrame(data, columns=["Data", "Brutto", "Transakcja"])
                                    prices_df["Data"]=pd.to_datetime(prices_df["Data"], dayfirst=True, format="%d-%m-%Y").dt.date
                                    prices_df["Brutto"]=prices_df["Brutto"].str.replace("zł ","").str.replace(",",".").astype("float")
                                    prices_df["Netto"]=round((prices_df["Brutto"]/123)*100,2)
                                    prices_df["VAT"]=round((prices_df["Netto"]*0.23),2)
                                    prices_df.sort_values("Data")
                                    dfs_list.append(prices_df)                      

        final_df=pd.concat(dfs_list)
        final_df=final_df.reset_index().drop("index", axis=1)
        final_df["Transakcja"]=final_df["Transakcja"].astype("int")
        final_df.drop_duplicates(subset="Transakcja", inplace=True)
        return final_df

    def parse_pdfs(self, invoices_list):
        context=ssl.create_default_context()
        dfs_list=[]
        for file in sorted(os.listdir(self.invoices_dir)):
            if file !=".DS_Store":
                path=os.path.join(self.invoices_dir, file)
                pdf_doc= fitz.open(path)
                page=pdf_doc.load_page(0)
                text = page.get_text("text")
                invoice_text="Numer:"
                transact_text="Nr dok.wydania:"
                invoice_pos = text.find(invoice_text)
                transact_pos = text.find(transact_text)
                invoice_text_beg=invoice_pos+len(invoice_text)+1
                transact_text_beg=transact_pos+len(transact_text)+1
                new_line_invoice=text[invoice_text_beg:invoice_text_beg+18].rfind("\n")
                if invoice_pos!=-1 and transact_pos!=-1:
                    invoice_number=text[invoice_text_beg:invoice_text_beg+new_line_invoice]
                    transact_number=text[transact_text_beg:transact_text_beg+9]
                    numbers=[[invoice_number, transact_number]]
                    numbers_df=pd.DataFrame(numbers, columns=["Faktura", "Transakcja"])
                    dfs_list.append(numbers_df)

                    if invoice_number not in invoices_list:
                        msg = MIMEMultipart()
                        msg['Subject'] = f"Faktura Paliwo: {invoice_number}"
                        msg['From'] = conf.email_user
                        msg['To'] = conf.email_user
                        body="W załączeniu faktura\n"
                        body_part = MIMEText(body)
                        msg.attach(body_part)

                        with open(path,'rb') as pdf_file:
                            msg.attach(MIMEApplication(pdf_file.read(), Name=file))

                        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                            smtp.login(conf.email_user, conf.email_password)
                            smtp.sendmail(conf.email_user, conf.email_reciever, msg.as_string())

        final_df=pd.concat(dfs_list)
        final_df=final_df.reset_index().drop("index", axis=1)
        final_df["Transakcja"]=final_df["Transakcja"].astype("int")
        final_df.drop_duplicates(subset=["Faktura", "Transakcja"],inplace=True)
        invoices_count=final_df.shape[0]
        return final_df, invoices_count

    def get_merged_df(self, invoices_list):
        prices_df=self.get_mails()
        numbers_df, invoices_count=self.parse_pdfs(invoices_list)
        merged_df=numbers_df.merge(prices_df, "inner", left_on="Transakcja", right_on="Transakcja")
        merged_df=merged_df[["Data", "Faktura", "Netto", "VAT", "Brutto"]]
        return merged_df, invoices_count

class Sheet:
    def __init__(self):
        self.sheet_id="1oZKBbqcYV6NMcrzE8SBqFpNrVt1w6pLMmUf62JqX_D8"
        self.gc = gspread.service_account(filename='/Users/wojtekmarszalek/Desktop/Osobiste/Nauka/Python/PythonScripts/Personal/Petrol_Invoices/invoices_automatation.json') 
        self.sh = self.gc.open_by_url(f'https://docs.google.com/spreadsheets/d/{self.sheet_id}')
        self.worksheet = self.sh.worksheet("Faktury")

    def get_sheet_invoices_list(self):
        sheets_df = get_as_dataframe(self.worksheet, True)
        sheets_df=sheets_df.iloc[:,:-3]
        sheets_df["Data"]=pd.to_datetime(sheets_df["Data"], dayfirst=True, format='mixed').dt.date
        self.invoices_list=sheets_df["Faktura"].to_list()
        return sheets_df

    def update_google_sheet(self, sheets_df, merged_df):
        df_update=pd.concat([sheets_df, merged_df])
        df_update.sort_values("Data", inplace=True)
        df_update.drop_duplicates(["Data", "Faktura"], inplace=True)
        set_with_dataframe(self.worksheet, df_update)

    def send_reminder(self):
        context=ssl.create_default_context()
        sh=self.sh
        worksheet = sh.worksheet("Faktury")
        sheets_df = get_as_dataframe(worksheet, True)
        vat_to_pay=round(sheets_df.iloc[0,-3],2)
        if vat_to_pay>0:
            subject="Przypomnienie"
            body=f"""
            Masz do uregulowania zaległą płatność w kwocie: {vat_to_pay}
            """
            msg=EmailMessage()
            msg["From"]=conf.email_user
            msg["To"]=conf.email_reciever
            msg["Subject"]=subject
            msg.set_content(body)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(conf.email_user, conf.email_password)
                smtp.sendmail(conf.email_user, conf.email_reciever, msg.as_string())

if __name__=="__main__":
    logging.basicConfig(
     filename=conf.log_file,
     level=logging.INFO, 
     format= '[%(asctime)s] {%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S')
    
    logging.info("--------Script Started----------")
    mail=Mail()
    sheet=Sheet()
    sheets_df=sheet.get_sheet_invoices_list()
    merged_df, invoices_count=mail.get_merged_df(sheet.invoices_list)
    logging.info(f"Fetched mails: {invoices_count}")
    sheet.update_google_sheet(sheets_df, merged_df)
    sheet.send_reminder()
    logging.info("--------Script finished----------")
