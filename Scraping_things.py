import time
from datetime import datetime
import Global_var
from Insert_On_Datbase import insert_in_Local
import sys , os
import string
import time
from datetime import datetime
import html
import re
import wx
app = wx.App()

def remove_html_tag(string):
    cleanr = re.compile('<.*?>')
    main_string = re.sub(cleanr, '', string)
    return main_string

def scrap_data(Tender_link,Tender_deadline,get_htmlsource,notice_number):

    SegField = []
    for data in range(42):
        SegField.append('')
    
    a = True
    while a == True:
        try:
            Email = get_htmlsource.partition('Sähköpostiosoite </div>')[2].partition("</div>")[0].strip()
            Email = remove_html_tag(Email)
            SegField[1] = Email.strip()
            
            name_and_address = get_htmlsource.partition('Nimi ja osoitteet</span>')[2].strip()

            buyer_name = name_and_address.partition('Virallinen nimi </div>')[2].partition("</div>")[0].strip()
            buyer_name = remove_html_tag(buyer_name)

            SegField[12] = buyer_name

            Postal_address = name_and_address.partition('Postiosoite </div>')[2].partition("</div>")[0].strip()
            Postal_address = remove_html_tag(Postal_address)

            Postal_code = name_and_address.partition('Postinumero </div>')[2].partition("</div>")[0].strip()
            Postal_code = remove_html_tag(Postal_code)

            Town = name_and_address.partition('Postitoimipaikka </div>')[2].partition("</div>")[0].strip()
            Town = remove_html_tag(Town)

            country =  name_and_address.partition('Maa </div>')[2].partition("</div>")[0].strip()
            country = remove_html_tag(country)

            telphone =  get_htmlsource.partition('Puhelin </div>')[2].partition("</div>")[0].strip()
            telphone = remove_html_tag(telphone)
            if Postal_address == '':
                Proper_address = f'{buyer_name}<br>\n{Town.strip()},{country.strip()} - {Postal_code.strip()}, Tel: {telphone.strip()}'
                Proper_address = string.capwords(str(Proper_address))
                SegField[2] = Proper_address.strip()
            elif country == '':
                Proper_address = f'{buyer_name}<br>\n{Postal_address.strip()},{Town.strip()},Finland - {Postal_code.strip()}, Tel: {telphone.strip()}'
                Proper_address = string.capwords(str(Proper_address))
                SegField[2] = Proper_address.strip()
            elif Postal_code == '':
                Proper_address = f'{buyer_name}<br>\n{Postal_address.strip()},{Town.strip()},{country.strip()} , Tel: {telphone.strip()}'
                Proper_address = string.capwords(str(Proper_address))
                SegField[2] = Proper_address.strip()
            elif telphone == '':
                Proper_address = f'{buyer_name}<br>\n{Postal_address.strip()},{Town.strip()},{country.strip()} - {Postal_code.strip()}'
                Proper_address = string.capwords(str(Proper_address))
                SegField[2] = Proper_address.strip()
            else:
                Proper_address = f'{buyer_name}<br>\n{Postal_address.strip()}, {Town.strip()}, {country.strip()} - {Postal_code.strip()}, Tel: {telphone.strip()}'
                Proper_address = string.capwords(str(Proper_address))
                SegField[2] = Proper_address.strip()

            purchase_url = get_htmlsource.partition('Verkko-osoite')[2].partition("</a>")[0].strip()
            purchase_url = purchase_url.partition('href="')[2].partition('"')[0].strip()
            SegField[8] = purchase_url.strip()
            
            Title =  get_htmlsource.partition('Hankinnan nimi </div>')[2].partition("</div>")[0].strip()
            Title = remove_html_tag(Title)
            Title = string.capwords(str(Title))
            SegField[19] = Title.strip()

            Tender_detail = get_htmlsource.partition('Hankinnan lyhyt kuvaus')[2].partition('class="notice-public-standard')[0].strip()
            Tender_detail = Tender_detail.partition('class="value-row-value')[2]
            Tender_detail = remove_html_tag(Tender_detail)
            Tender_detail = Tender_detail.partition('">')[2].partition('<div')[0].strip()
            Tender_detail = string.capwords(str(Tender_detail))
            if len(Tender_detail) >= 800:
                Tender_detail = str(Tender_detail)[:800]+'...'
                Tender_detail = string.capwords(str(Tender_detail))
            Type_of_contract = get_htmlsource.partition('Sopimuksen tyyppi</div></div>')[2].partition('</div>')[0].strip()
            Type_of_contract = remove_html_tag(Type_of_contract)
            Type_of_contract = string.capwords(str(Type_of_contract))

            NUTS_code = get_htmlsource.partition('NUTS-koodi</div>')[2].partition('</span>')[0].strip()
            NUTS_code = remove_html_tag(NUTS_code)
            if len(NUTS_code) >= 25:
                NUTS_code = ''

            Type_of_procedure = get_htmlsource.partition('Menettelyn luonne </div>')[2].partition('</div>')[0].strip()
            Type_of_procedure = remove_html_tag(Type_of_procedure)
            Type_of_procedure = string.capwords(str(Type_of_procedure))

            SegField[18] = f'{SegField[19]}<br>\nSLyhyt kuvaus: {Tender_detail.strip()}<br>\nSopimuksen tyyppi: {Type_of_contract.strip()}<br>\nNUTS-koodi: {NUTS_code.strip()}<br>\nMenettelyn luonne: {Type_of_procedure.strip()}'


            SegField[13] = notice_number.strip()

            SegField[14] = '2'
            SegField[22] = "0"
            SegField[26] = "0.0"
            SegField[27] = "0"  # Financier
            SegField[24] = Tender_deadline.strip()
            SegField[7] = 'FI'
            SegField[28] = Tender_link
            SegField[31] = 'hankintailmoitukset.fi'

            ReplyStrings = get_htmlsource.partition('CPV-koodi</div></div>')[2].partition("</div>")[0].strip()
            ReplyStrings = remove_html_tag(ReplyStrings)
            if ReplyStrings != "":
                copy_cpv = ""
                Cpv_status = True
                all_string = ""
                try:
                    while Cpv_status == True:
                        phoneNumRegex = re.compile(r'\d\d\d\d\d\d\d\d')
                        CPv_main = phoneNumRegex.search(ReplyStrings)
                        mainNumber = CPv_main.groups()
                        if CPv_main:
                            copy_cpv = CPv_main.group(), ", "
                            ReplyStrings = ReplyStrings.replace(CPv_main.group(), "")
                        else:
                            Cpv_status = False
                        result = "".join(str(x) for x in copy_cpv)
                        result = result.replace("-", "").strip()
                        result2 = result.replace("\n", "")
                        # print(result2)
                        all_string += result2.strip(",")
                except:
                    pass
                print(all_string.strip(","))
                SegField[36] = all_string
            else:
                SegField[36] = ""

            for SegIndex in range(len(SegField)):
                print(SegIndex, end=' ')
                print(SegField[SegIndex])
                SegField[SegIndex] = html.unescape(str(SegField[SegIndex]))
                SegField[SegIndex] = str(SegField[SegIndex]).replace("'", "''")

            if len(SegField[19]) >= 200:
                SegField[19] = str(SegField[19])[:200]+'...'

            if len(SegField[18]) >= 1500:
                SegField[18] = str(SegField[18])[:1500]+'...'

            if SegField[19] == '':
                wx.MessageBox(' Short Desc Blank ','hankintailmoitukset.fi', wx.OK | wx.ICON_INFORMATION)
            else:
                check_date(get_htmlsource, SegField)
                pass

            a = False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",
                  exc_tb.tb_lineno)
            a = True
            time.sleep(5)


def check_date(get_htmlSource, SegField):
    deadline = str(SegField[24])
    curdate = datetime.now()
    curdate_str = curdate.strftime("%Y-%m-%d")
    try:
        if deadline != '':
            datetime_object_deadline = datetime.strptime(deadline, '%Y-%m-%d')
            datetime_object_curdate = datetime.strptime(curdate_str, '%Y-%m-%d')
            timedelta_obj = datetime_object_deadline - datetime_object_curdate
            day = timedelta_obj.days
            if day > 0:
                insert_in_Local(get_htmlSource, SegField)
            else:
                print("Expired Tender")
                Global_var.expired += 1
        else:
            print("Deadline Not Given")
            Global_var.deadline_Not_given += 1
    except Exception as e:
        exc_type , exc_obj , exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" , fname , "\n" ,exc_tb.tb_lineno)