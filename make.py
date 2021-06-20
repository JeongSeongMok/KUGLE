import urllib.request as r
import pymysql
import urllib.parse as p
import json
import pandas as pd
import ssl
import _jpype
import konlpy
import math
from konlpy.tag import Kkma, Komoran, Hannanum, Okt
from konlpy.utils import pprint

db = pymysql.connect(
    user = 'root',
    passwd='4242',
    host='localhost',
    db='news',
    charset='utf8mb4'
)
inverted_wordlist =[]
cursor = db.cursor()
url = "https://kubic.handong.edu:15000/retrieve_all?"
serviceKey = 'KEY값 입력'
numOfCnt = 200
ID_input = 1;
okt = Okt()
for page in range(1,49):
    option = "serviceKey="+serviceKey
    request = ""
    request = "&numOfCnt="+p.quote(str(numOfCnt))+"&page="+p.quote(str(page))
    url_full = url + option + request

    context = ssl._create_unverified_context()
    response = r.urlopen(url_full,context=context).read().decode('utf-8')

    jsonArray = json.loads(response) 

    if jsonArray.get("header").get("resultCode") != 200:
        print("Error!!!")
        print(jsonArray.get("header"))
        quit()

    items =jsonArray.get("body").get("contents")

    df = pd.DataFrame(columns=['title','body','writer','date','institution','institutionURL','fileURL','fileName','fileContent'])
    a=0
    for item in items :
        df = df.append(item,ignore_index=True)
        a+=1
    sql_art = "insert into article (id, title, writer, date,file_URL, file_Name,inst_Name,inst_URL) values(%s, %s, %s, %s, %s, %s, %s, %s)"
    sql_con = "insert into contents (id, body) values (%s, %s)"
    sql_inv = "insert into inverted (word, id, search_count) values (%s, %s, %s)"
    sql_view = "insert into view (id, view_count) values (%s, %s)"
    for u in range(0,numOfCnt):
        date_temp=''
        if df['date'][u] is None:
            date_temp= " "
        else :
            date_temp = df['date'][u] 
        wr_temp=''
        if df['writer'][u] is None:
            wr_temp= " "
        else :
            wr_temp = df['writer'][u]
        fu_temp=''
        if df['fileURL'][u] is None:
            fu_temp= 'NULL'
        else :
            fu_temp = df['fileURL'][u]
        fn_temp=''
        if df['fileName'][u] is None:
            fn_temp= 'NULL'
        else :
            fn_temp = df['fileName'][u]
        iu_temp=''
        if df['institutionURL'][u] is None:
            iu_temp= 'NULL'
        else :
            iu_temp = df['institutionURL'][u]
        in_temp=''
        if df['institution'][u] is None:
            in_temp= 'NULL'
        else :
            in_temp = df['institution'][u]   
        body_temp=''
        if df['body'][u] is None:
            if df['fileContent'][u] is None:
                body_temp = " "
            else : 
                body_temp = df['fileContent'][u]
        else :
            body_temp = df['body'][u]   
        wordlist = okt.nouns(body_temp)
        val_art=(ID_input, df['title'][u],wr_temp,date_temp,fu_temp,fn_temp,in_temp,iu_temp)
        sql_if_a = "SELECT COUNT(id) FROM article A WHERE A.date=%s AND A.writer=%s AND A.title=%s;"
        val_if_a = (date_temp, wr_temp, df['title'][u])
        cursor.execute(sql_if_a,val_if_a)
        result_temp1 = cursor.fetchall()
        if(result_temp1[0][0]==0) :
            cursor.execute(sql_art,val_art)
            cursor.execute(sql_con, (ID_input,body_temp))
            cursor.execute(sql_view, (ID_input, 0))
            db.commit()

            for wordindex in range(0,len(wordlist)):
                sql_if_i1 = "SELECT COUNT(id) FROM inverted I WHERE I.word=%s;"
                cursor.execute(sql_if_i1, (wordlist[wordindex]))
                result_temp3 = cursor.fetchall()
                if(result_temp3[0][0]==0) :
                    inverted_wordlist.append(wordlist[wordindex])
                sql_if_i2 ="SELECT COUNT(id) FROM inverted I WHERE I.word=%s AND I.id = %s;"
                val_up_i = (wordlist[wordindex], ID_input)
                cursor.execute(sql_if_i2, val_up_i)
                result_temp2 =cursor.fetchall()
                if(result_temp2[0][0]>0) : 
                    sql_up_i = "UPDATE inverted I SET I.search_count = I.search_count+1 WHERE I.word = %s AND I.id = %s;"
                    cursor.execute(sql_up_i, val_up_i)
                    db.commit()
                else :
                    val_inv = (wordlist[wordindex], ID_input, 1)
                    cursor.execute(sql_inv, val_inv)
                    db.commit()
            ID_input+=1 

print(ID_input)  
