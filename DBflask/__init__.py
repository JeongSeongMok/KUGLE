from flask import Flask, g, request,  make_response, Response, render_template
import pymysql
import pandas as pd
import math
#flask 이름 생성i
res=[]

app = Flask(__name__)
app.debug = True
db = pymysql.connect(
    user = 'root',
    passwd='4242',
    host='localhost',
    db='news',
    charset='utf8mb4'
)
ID_input = 8901
cursor = db.cursor()
tf_idf = pd.DataFrame(columns = ['ID'])
sql_if_i1 = "SELECT word FROM inverted;"
sql_if_i3 = "SELECT COUNT(id) FROM inverted I WHERE I.word=%s;" 

cursor.execute(sql_if_i1)
result_temp3 = cursor.fetchall()
tempstr = ""
for i in range(0,len(result_temp3)):
    if (tempstr != result_temp3[i][0]) : 
        tf_idf[result_temp3[i][0]]=0
    tempstr = result_temp3[i][0]

tf_idf = tf_idf.append({'ID':0},ignore_index=True)
for i in range(1, len(tf_idf.columns)):
    cursor.execute(sql_if_i3, (tf_idf.columns[i]))
    count_temp = cursor.fetchall()
    tf_idf.loc[0, tf_idf.columns[i]]=math.log(ID_input-1/(count_temp[0][0]+1))
for i in range(1, ID_input):
        tf_idf = tf_idf.append({'ID':i},ignore_index=True)
        for j in range(1, len(tf_idf.columns)):
            tf_idf.loc[i,tf_idf.columns[j]]=0

cursor.execute("SELECT * FROM inverted;")
inv = cursor.fetchall()
ind = 0
tempstr =""

for i in range(0, len(inv)) :
    if(tempstr != inv[i][0]):
         ind = ind+1
    tf_idf.loc[inv[i][1], tf_idf.columns[ind]] = inv[i][2]*tf_idf.loc[0,tf_idf.columns[ind]]
    tempstr = inv[i][0]

#app.before_request
#def before_request():
    #print("before_request")
    #g.str = "한글"
    #접속자 수를 여기에 넣는다던지 하면 된다.
    #g의 값을 제어하면서 수시로 변경 가능

#route가 URI를 정의하는 것을 route
#실행되는 놈이고
@app.route('/', methods=['GET']) # main page
def index():
    return render_template('/index.html')

@app.route('/error', methods=['GET', 'POST']) 
def error():
    return render_template('/error.html')

@app.route('/search', methods=['GET'])
def search():
    global res
    mycursor = db.cursor()
    id = int(request.url.split('?')[1])
    sql = "UPDATE view SET view_count=view_count+1 WHERE id="
    sql += str(res[id]['id'])
    sql += ';'
    mycursor.execute(sql)

    db.commit()

    sql2 = "SELECT view_count FROM view WHERE id="
    sql2 += str(res[id]['id'])
    sql2 += ';'
    mycursor.execute(sql2)
    q_res = mycursor.fetchall()
    count_res=[]
    count_res.append(dict(zip(['count'], list(q_res[0]))))    

    return render_template('/search.html', result=res[id], count = count_res[0]['count'])

@app.route('/main', methods=['POST', 'GET'])
def main():
    # option = 저자
    global res
    res = []
   
    if request.method == 'POST':
        val = request.form #addrbook.html에서 name을 통해 submit한 값들을 val 객체로 전달
        if val['contents'] == None or val['contents'] =='':
            return render_template('/error.html', contents=val['contents'], contents_opt=val['options'])
        
        if val['options'] == '저자':
            
            sql = "SELECT * FROM article A JOIN (contents C, view V) WHERE A.writer LIKE '%"+val['contents']+"%' AND A.id=C.id AND V.id = A.id;"

            cursor.execute(sql)

            query_result = cursor.fetchall()
            
            key_list=['id', 'title', 'writer', 'date', 'file_URL', 'file_Name', 'inst_Name', 'inst_URL', 'id','body','id','view_count']
            
            for i in range(len(query_result)):
                res.append(dict(zip(key_list, list(query_result[i]))))
            if not res:
                return render_template('/error.html', contents=val['contents'], contents_opt=val['options'])
           # print(res)
            return render_template('/main.html',result=res, contents=val['contents'], contents_opt=val['options'], length=len(res))
        elif val['options']=='내용':
            temp = val['contents'].split()
            #for i in range(1, ID_input):
            s_index = []
            sort_temp = pd.DataFrame(columns = ['ID', 'SUM'])

            for i in range(0, len(tf_idf.columns)):
                if tf_idf.columns[i] in temp:
                    s_index.append(i)
            
            for i in range (1, len(tf_idf)):
                sum=0
                for j in range (0,len(s_index)):
                    index_temp = s_index[j]
                    sum = sum+ tf_idf.loc[i,tf_idf.columns[index_temp]]
                sort_temp = sort_temp.append({'ID':i, 'SUM':sum},ignore_index=True)
            sort_temp.sort_values(by=['SUM'],axis=0,ascending=False, inplace=True)
            sort_temp = sort_temp.reset_index(drop=True)
            #print(sort_temp)
            key_list=['id', 'title', 'writer', 'date', 'file_URL', 'file_Name', 'inst_Name', 'inst_URL', 'id','body','id','view_count']
            res=[]
            query_result=[]
            for i in range (0,len(sort_temp)):
                if (sort_temp.loc[i, 'SUM']==0) :
                    break
                id_temp = int(sort_temp.loc[i,'ID'])
                #print(id_temp)
                sql = "SELECT * FROM article A JOIN (contents C, view V) WHERE A.id=%s AND A.id=C.id AND A.id = V.id;"    
                cursor.execute(sql,(id_temp))
                query_result = query_result+list(cursor.fetchall())
            query_result = tuple(query_result)
            #print(query_result)
            #print(type(query_result))
            for i in range(len(query_result)):
                res.append(dict(zip(key_list, list(query_result[i]))))
            if not res:
                return render_template('/error.html', contents=val['contents'], contents_opt=val['options'])
            return render_template('/main.html',result=res, contents=val['contents'], contents_opt=val['options'], length=len(res), con=str(val['contents']))
        else:
            sql = "SELECT * FROM article A JOIN (contents C, view V) WHERE A.title LIKE '%"+val['contents']+"%' AND A.id=C.id AND V.id=A.id;"
            cursor.execute(sql)
            query_result = cursor.fetchall()
            
            key_list=['id', 'title', 'writer', 'date', 'file_URL', 'file_Name', 'inst_Name', 'inst_URL', 'id','body','id','view_count']
            for i in range(len(query_result)):
                res.append(dict(zip(key_list, list(query_result[i]))))
            if not res:
                return render_template('/error.html', contents=val['contents'], contents_opt=val['options'])
            return render_template('/main.html',result=res, contents=val['contents'], contents_opt=val['options'], length=len(res))
    else:
        return render_template('/main.html', result="POST가 아님", contents='known', length=0)

