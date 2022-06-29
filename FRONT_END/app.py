from sre_parse import WHITESPACE
from flask import Flask, flash, render_template, request,redirect,url_for
import psycopg2

app = Flask(__name__)

def get_connect():
    host = 'ec2-3-224-8-189.compute-1.amazonaws.com'
    database = 'ddutpjpqn1gmhm'
    user = 'etaykzhvlemujo'
    port = '5432'
    password = '3093a22e274ea68ce68239bc2f3c2513dedafb464a3a0815839a7d0c0994c697'
    #Then created the connection using the above:
    
    conn = psycopg2.connect(database=database,
        user=user,
        password=password,
        host=host,
        port=port)
    return conn

@app.route("/", methods = ['GET','POST'])
def hello_world():
    conn = get_connect()
    cur = conn.cursor()

    death = []
    cases = []
    cur.execute("SELECT * FROM country_data where ISO3 = 'Global' ;")
    totaldata = cur.fetchall()
    death.append(totaldata[0][4])
    death.append(totaldata[0][5])
    cases.append(totaldata[0][2])
    cases.append(totaldata[0][3])
    
    
    cur.execute("SELECT sum(New_deaths) FROM global_data where Date_reported = (SELECT MAX(Date_reported) FROM global_data) ;")
    lastdeath = cur.fetchall()
    death.append(lastdeath[0][0])
    
    cur.execute("SELECT sum(New_cases) FROM global_data where Date_reported = (SELECT MAX(Date_reported) FROM global_data) ;")
    lastcases = cur.fetchall()
    cases.append(lastcases[0][0])


    cur.execute('SELECT * FROM topdeaths;')
    Top5Death = cur.fetchall()
    
    cur.execute('SELECT * FROM topcases;')
    Top5Case = cur.fetchall()
    
    cur.execute("SELECT * FROM region_data;")
    WHO_Region = cur.fetchall()
    
    #close connection 
    cur.close()
    conn.close()


    return render_template('Main.html',death = death ,case =cases,T5D = Top5Death,T5C = Top5Case,who = WHO_Region)

@app.route("/login", methods = ['GET','POST'])
def login():
    conn = get_connect()
    cur = conn.cursor()
    if request.method == 'POST':
        user = request.form['username']
        pas = request.form['password']
        str = f"SELECT * from login where username = '{user}' and password = '{pas}';"
        cur.execute(str)
        data = cur.fetchall()
        #print(data)
        if len(data) == 0:
            cur.close()
            conn.close()
            flash('incorrect username and password')
            return render_template('login.html')
        else:
            print('data found')
    cur.close()
    conn.close()

    return redirect(url_for('admin'))

@app.route("/login-enter")
def loginenter():
    return render_template('login.html')

@app.route("/admin/insert", methods = ['GET','POST'])
def admin_insert():
    conn = get_connect()
    cur = conn.cursor()
    if request.method == 'POST':
        date = request.form['date1']
        country = request.form['country1']
        case = request.form['case1']
        death = request.form['death1']
        #country = '%'+country+'%'
        sql="SELECT * from global_data g, countries c  where g.Country_code = c.ISO2 and c.Name like  %s limit 5;"
        args=['%'+country+'%']
        cur.execute(sql,args)
        check = cur.fetchall()
        print(check)
        if len(check)==0:
            cur.close()
            conn.close()
            flash('Invalid Country')
            return render_template('admin_insert.html')
        sql="SELECT * from global_data g, countries c  where g.Date_reported = %s and g.Country_code = c.ISO2 and c.Name like %s;"
        args= [date,'%'+country+'%']
        cur.execute(sql,args)
        check = cur.fetchall()
        print(check)
        if len(check)!=0:
            cur.close()
            conn.close()
            flash('Data already Present')
            return render_template('admin_insert.html')
        cur.callproc('insert_data',[date,country,case,death,])
        #cur.commit()
        cur.close()
        conn.close()
        flash('Data sucessfully Inserted')
        return render_template('admin_insert.html')
        
    return render_template('admin.html')

@app.route("/admin/update", methods = ['GET','POST'])
def admin_update():
    conn = get_connect()
    cur = conn.cursor()
    if request.method == 'POST':
        date = request.form['date2']
        country = request.form['country2']
        case = request.form['case2']
        death = request.form['death2']
        #country = '%'+country+'%'
        sql="SELECT * from global_data g, countries c  where g.Country_code = c.ISO2 and c.Name like  %s limit 5;"
        args=['%'+country+'%']
        cur.execute(sql,args)
        check = cur.fetchall()
        print(check)
        if len(check)==0:
            cur.close()
            conn.close()
            flash('Invalid Country')
            return render_template('admin_update.html')
        sql="SELECT * from global_data g, countries c  where g.Date_reported = %s and g.Country_code = c.ISO2 and c.Name like %s;"
        args= [date,'%'+country+'%']
        cur.execute(sql,args)
        check = cur.fetchall()
        if len(check)==0:
            cur.close()
            conn.close()
            flash('No Data for given Date')
            return render_template('admin_update.html')
        cur.callproc('update_data',[date,country,case,death,])
        #cur.commit()
        cur.close()
        conn.close()
        flash('Data sucessfully Updated')
        return render_template('admin_update.html')
        
    return render_template('admin.html')

@app.route("/admin/vaccine", methods = ['GET','POST'])
def admin_vaccine():
    conn = get_connect()
    cur = conn.cursor()
    if request.method == 'POST':
        country = request.form['country3']
        vaccine = request.form['vac']
        product = request.form['prod']
        company = request.form['comp']
        auth = request.form['auth']
        start = request.form['start']
        end = request.form['end']
        comment = request.form['comment']
        #country = '%'+country+'%'
        sql="SELECT * from  countries c  where  c.Name like  %s limit 5;"
        args=['%'+country+'%']
        cur.execute(sql,args)
        check = cur.fetchall()
        print(check)
        if len(check)==0:
            cur.close()
            conn.close()
            flash('Invalid Country')
            return render_template('admin_vaccine.html')
        sql="SELECT * from vaccine_metadata v, countries c  where v.ISO3 = c.ISO3 and c.Name like  %s and v.VACCINE_NAME = %s;"
        args=['%'+country+'%',vaccine]
        cur.execute(sql,args)
        check = cur.fetchall()
        print(check)
        if len(check)!=0:
            cur.close()
            conn.close()
            flash('Same product already registered for country')
            return render_template('admin_vaccine.html')
        sql="SELECT * FROM countries WHERE Name like  %s;"
        args=['%'+country+'%']
        cur.execute(sql,args)
        check = cur.fetchall()
        sql="INSERT INTO vaccine_metadata values(%s,%s,%s,%s,%s,%s,%s,%s,'OWID');"
        args= [check[0][2],vaccine,product,company,auth if len(auth)!=0 else None,start if len(start)!=0 else None ,end if len(end)!=0 else None,comment if len(comment)!=0 else None]
        cur.execute(sql,args)
        #cur.commit()
        cur.close()
        conn.close()
        flash('Vaccine sucessfully Added')
        return render_template('admin_vaccine.html')
        
    return render_template('admin.html')

@app.route("/admin", methods = ['GET','POST'])
def admin():
    return render_template('admin.html')

@app.route("/country/<string:name>", methods = ['GET','POST'])
def search(name):
    conn = get_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM countries where Name = %s;",[name])
    code = cur.fetchall()
    sql = "SELECT * FROM country_data where ISO3 = %s;"
    args = [code[0][2]]
    cur.execute(sql,args)
    temp = cur.fetchall()
    country_info = temp[0]
    sql = "SELECT * FROM global_data where Date_reported = (SELECT MAX(Date_reported) FROM global_data)  and Country_code = %s;"
    args = [code[0][1]]
    cur.execute(sql,args)
    temp = cur.fetchall()
    new_info = []
    new_info.append(temp[0][3])
    new_info.append(temp[0][5])
    sql = "SELECT * FROM vaccine_data where ISO3 = %s;"
    args = [code[0][2]]
    cur.execute(sql,args)
    temp = cur.fetchall()
    vaccine_info = temp[0]
    sql = "SELECT * FROM vaccine_metadata where ISO3 = %s;"
    args = [code[0][2]]
    cur.execute(sql,args)
    metadata = cur.fetchall()
    sql = "SELECT * FROM who_region where Code = %s;"
    args = [country_info[1]]
    cur.execute(sql,args)
    temp= cur.fetchall()
    names = [name,temp[0][1]]
    cur.close()
    conn.close()
    return render_template('search.html',names = names,country_info = country_info,new_info = new_info,vaccine_info = vaccine_info,metadata = metadata)

@app.route("/country", methods = ['GET','POST'])
def country():
    conn = get_connect()
    cur = conn.cursor()
  

    cur.execute("SELECT c.*,cc.Name FROM country_data c ,countries cc where cc.ISO3 = c.ISO3 and cc.Name not in ('World','Others'); ")
    Country_data1 = cur.fetchall()

    #close connection 
    cur.close()
    conn.close()
    

    return render_template('country.html',c_data = Country_data1)












@app.route("/dummy", methods = ['GET','POST'])
def dummy():
    conn = get_connect()
    cur = conn.cursor()

    
    
    cur.callproc('insert_data',['2022-02-18','Afghanistan',23,2,])
    #cur.commit()
    WHO_Region = cur.fetchall()
    print(WHO_Region)
    #close connection 
    cur.close()
    conn.close()


    return render_template('search.html')
 

if __name__ == "__main__":
    app.secret_key = "This is just secret key"
    app.run(port = 5432 ,debug=True)
