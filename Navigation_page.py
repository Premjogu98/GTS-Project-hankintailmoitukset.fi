from selenium import webdriver
import time
import html
import sys, os
from datetime import datetime,timedelta
import Global_var
import wx
import string
import html
import re
from Scraping_things import scrap_data
import urllib.request
import urllib.parse
import requests

app = wx.App()

def ChromeDriver():
    browser = webdriver.Chrome(executable_path=str(f"C:\\chromedriver.exe"))

    browser.get("https://www.hankintailmoitukset.fi/en/search")
    browser.maximize_window()
    time.sleep(5)
    Tender_count = ''
    for Tender_count in browser.find_elements_by_xpath('//*[@class="search-result-count p-3 px-4"]/strong'):
        Tender_count = Tender_count.get_attribute('innerText').strip()
        break
    TenderDeadline_list = []
    count = 0
    for tr in range(1, int(Tender_count), 1):
        for published in browser.find_elements_by_xpath(f'/html/body/div[1]/main/div/div/div[2]/div/table/tbody/tr[{str(tr)}]/td[3]/span'):
            published = published.get_attribute('innerText').strip()
            break
        datetime_object = datetime.strptime(published, '%d.%m.%Y %H:%M')
        publish_date = datetime_object.strftime("%d-%m-%Y")

        datetime_object_pub = datetime.strptime(publish_date, '%d-%m-%Y')
        User_Selected_date = datetime.strptime(str(Global_var.From_Date), '%d-%m-%Y')

        timedelta_obj = datetime_object_pub - User_Selected_date
        day = timedelta_obj.days
        
        if day >= 0:
            for FI_EU_Condition in browser.find_elements_by_xpath(f'/html/body/div[1]/main/div/div/div[2]/div/table/tbody/tr[{str(tr)}]/td[1]/span'):
                FI_EU_Condition = FI_EU_Condition.get_attribute('innerText').strip()
                break
            if FI_EU_Condition == 'FI':
                Tender_link = ''
                Tender_Deadline = ''
                for Tender_link in browser.find_elements_by_xpath(f'/html/body/div[1]/main/div/div/div[2]/div/table/tbody/tr[{str(tr)}]/td[2]/a'):
                    Tender_link = Tender_link.get_attribute('href').strip()
                    break
                for Tender_Deadline in browser.find_elements_by_xpath(f'/html/body/div[1]/main/div/div/div[2]/div/table/tbody/tr[{str(tr)}]/td[4]/span'):
                    Tender_Deadline = Tender_Deadline.get_attribute('innerText').strip()
                    break
                if Tender_Deadline != '':
                    datetime_object = datetime.strptime(Tender_Deadline, '%d.%m.%Y %H:%M')
                    Tender_Deadline = datetime_object.strftime("%Y-%m-%d")
                    TenderDeadline_list.append(f'{Tender_link}[]@#$%{Tender_Deadline}')
                    count += 1
                    print(f'Link Collect: {str(count)}')
                else:
                    print('Deadline Not Given')
        else:
            print('Publish Date Dead')
            break
    print(f"\nTotal Link Collected {len(TenderDeadline_list)}")

    navigation_things(TenderDeadline_list,browser)

def navigation_things(TenderDeadline_list,browser):
    for href in TenderDeadline_list:  # https://www.hankintailmoitukset.fi/fi/public/procurement/38936/notice/50890/[]@#$%2020-07-24'
        Tender_link = str(href).partition("[]@#$%")[0].strip()  # https://www.hankintailmoitukset.fi/fi/public/procurement/38936/notice/50890/
        Tender_deadline = str(href).partition("[]@#$%")[2].strip() # 2020-07-24
        browser.get(Tender_link)
        time.sleep(4)
        notice_number = ''
        for notice_number in browser.find_elements_by_xpath('//*[@class="header-subscript flex-column"]'):
            notice_number = notice_number.get_attribute('outerHTML').strip().replace('<!---->','').replace('-\t','').replace('-\n','').replace('\t','').replace('\n','')
            notice_number = html.unescape(str(notice_number))
            notice_number = re.sub(' +', ' ', str(notice_number))
            notice_number =  notice_number.partition('Ilmoituksen numero</span>')[2].partition("</span>")[0].strip()
            notice_number =  notice_number.partition('">')[2]
            break
        tab_links_list = []
        for tab_links in browser.find_elements_by_xpath('//*[@class="progress-nav categoryList nav nav-tabs pl-0"]/li/a'):
            tab_links_list.append(tab_links.get_attribute('href'))
            
        get_htmlsource = ''
        for tab_link in tab_links_list:
            browser.get(tab_link)
            time.sleep(3)
            pos = [] #list to store positions for each 'char' in 'string'
            for n in range(len(tab_link)):
                if tab_link[n] == '/':
                    pos.append(n)
            tab_link_class = tab_link[pos[-1]:]
            tab_link_class = tab_link_class.partition('/')[2].strip()
            tab_outerhtml = ''
            for tab_outerhtml in browser.find_elements_by_xpath(f'//*[@class="notice-public-{tab_link_class} card-body preview"]'):
                tab_outerhtml = tab_outerhtml.get_attribute('outerHTML').strip().replace('<!---->','').replace('-\t','').replace('-\n','').replace('\t','').replace('\n','')
                tab_outerhtml = html.unescape(str(tab_outerhtml))
                tab_outerhtml = re.sub(' +', ' ', str(tab_outerhtml))
                get_htmlsource += tab_outerhtml
        RM_button =  get_htmlsource.partition('<button')[2].partition("</button>")[0].strip()
        get_htmlsource = get_htmlsource.replace(RM_button,'').replace('<button','').replace('</button>','')
        scrap_data(Tender_link,Tender_deadline,get_htmlsource,notice_number)
        print(f'Total: {str(len(TenderDeadline_list))} Deadline Not given: {Global_var.deadline_Not_given} duplicate: {Global_var.duplicate} inserted: {Global_var.inserted} expired: {Global_var.expired} QC Tenders: {Global_var.QC_Tenders}')
    
    wx.MessageBox(f'Total: {str(len(TenderDeadline_list))}\nDeadline Not given: {Global_var.deadline_Not_given}\nduplicate: {Global_var.duplicate}\ninserted: {Global_var.inserted}\nexpired: {Global_var.expired}\nQC Tenders: {Global_var.QC_Tenders}','hankintailmoitukset.fi', wx.OK | wx.ICON_INFORMATION)
    browser.close()
    sys.exit() 


ChromeDriver()