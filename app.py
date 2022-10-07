from flask import Flask, render_template, request, jsonify, session
from flask_mysqldb import MySQL,MySQLdb 
from sqlassistance import *

app = Flask(__name__)
        
app.secret_key = "123456"
        
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'meter'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  

mysql = MySQL(app)
      
@app.route('/')
def index():
    return render_template('index.html')
 
@app.route("/ajaxlivesearch",methods=["POST","GET"])
def ajaxlivesearch():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    entries = Table("entries", "sl", "customer_id", "password", "encrypted", "decrypted", "d_customer_id", "unit", "time")
    if request.method == 'POST':
        search_entry = request.form.get('query')
        print(search_entry)
        if not search_entry:
            entries = entries.getalldesc()
            numrows = len(entries)
            print(numrows)
        else:    
            query = "SELECT * from entries WHERE customer_id LIKE '%{}%' OR time LIKE '%{}%' OR sl LIKE '%{}%' ORDER BY sl DESC LIMIT 1000".format(search_entry,search_entry,search_entry)
            cur.execute(query)
            numrows = int(cur.rowcount)
            entries = cur.fetchall()
            print(numrows)
    return jsonify({'htmlresponse': render_template('response.html', entries=entries, numrows=numrows)})
     
if __name__ == "__main__":
    app.run(debug=True)