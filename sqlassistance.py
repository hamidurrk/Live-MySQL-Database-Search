from app import mysql, session
import urllib.request as urllib2

webUrl = urllib2.urlopen("https://api.thingspeak.com/channels/1759095/fields/2/last.json")

class InvalidBillException(Exception): pass
class InsufficientFundsException(Exception): pass

class Table():
	def __init__(self, table_name, *args):
		self.table = table_name
		self.columns = "(%s)" %",".join(args)
		self.columnsList = args

		if checktable(table_name):              #checking if its a new table
			create_data = ""
			for column in self.columnsList:
				create_data += "%s varchar(100)," %column

			cur = mysql.connection.cursor() #create the table
			cur.execute("CREATE TABLE %s(%s)" %(self.table, create_data[:len(create_data)-1]))
			cur.close()

	def getall(self):                           #get all values from table
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM %s" %self.table)
		data = cur.fetchall(); return data
	
	def getalldesc(self):                       #get all values from table in descending order
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM %s ORDER BY sl DESC" %self.table)
		data = cur.fetchall(); return data

	def getlike(self, customer_id, time, sl):   #search db
		data = {}; cur = mysql.connection.cursor()
		result = cur.execute("SELECT * from %s WHERE customer_id LIKE  \"%s\" OR time LIKE \"%s\" OR sl LIKE \"%s\" ORDER BY sl DESC LIMIT 1000" %(self.table, customer_id, time, sl))
		if result > 0: data = cur.fetchone()
		cur.close(); return data

	def getone(self, search, value):            #get one value based on search
		data = {}; cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" %(self.table, search, value))
		if result > 0: data = cur.fetchone()
		cur.close(); return data

	def searchfromentry(self, entry, search, value):            #get one value based on condition	
		data = {}; cur = mysql.connection.cursor()
		result = cur.execute("SELECT %s FROM %s WHERE %s = \"%s\"" %(entry, self.table, search, value))
		if result > 0: data = cur.fetchone()
		cur.close(); return data

	def lastrowsl(self):            			#search for the serial of last row
		data = {}; cur = mysql.connection.cursor()
		result = cur.execute("SELECT sl FROM %s ORDER BY sl DESC LIMIT 1" %(self.table))
		if result > 0: data = cur.fetchone()
		cur.close(); return data

	def deleteone(self, search, value):         #delete one value
		cur = mysql.connection.cursor()
		cur.execute("DELETE from %s where %s = \"%s\"" %(self.table, search, value))
		mysql.connection.commit(); cur.close()

	def deleteall(self):                        #delete all values
		self.drop()                             #remove table and recreate
		self.__init__(self.table, *self.columnsList)

	def drop(self):                             #delete table entirely
		cur = mysql.connection.cursor()
		cur.execute("DROP TABLE %s" %self.table)
		cur.close()
	
	def resetorder(self):						#reset sl order
		cur = mysql.connection.cursor()
		cur.execute("set @count = 0")
		cur.execute("UPDATE %s SET %s.sl = @count:= @count +1" %(self.table, self.table))
		cur.close()

	def insert(self, *args):                    #insert data
		data = ""
		for arg in args: 						#convert data into string mysql format
			data += "\"%s\"," %(arg)

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO %s%s VALUES(%s)" %(self.table, self.columns, data[:len(data)-1]))
		mysql.connection.commit()
		cur.close()

	"""def update(self, entry, value, serial):      #update data
		cur = mysql.connection.cursor()
		cur.execute("UPDATE %s SET  %s = \"%s\" WHERE sl = \"%s\"" %(self.table, entry, value, serial))
		print("UPDATE %s SET  %s = \"%s\" WHERE sl = \"%s\"" %(self.table, entry, value, serial))
		cur.close() 
		"""



def sql_exe(execution):                         #for executing mysql code
	cur = mysql.connection.cursor()
	cur.execute(execution)
	mysql.connection.commit()
	cur.close()

def checktable(tableName):
	cur = mysql.connection.cursor()

	try:
		result = cur.execute("SELECT * from %s" %tableName) #try to read from the table
		cur.close()
	except:
		return True                                #if the table exist
	else:
		return False                               #if the table doesn't exist

def checkuser(username):                        
	users = Table("users", "name", "email", "username", "password")
	data = users.getall()
	usernames = [user.get('username') for user in data]

	return False if username in usernames else True

def checkmonth(month):    
	months = ['January', 'February', "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	return False if month in months else True

