import csv
import sys
import getpass
import MySQLdb
import datetime

################################################################################################################
#                                         Database Info                                                        #
################################################################################################################
SQL_HOST = 'localhost'
SQL_USER = 'root'
SQL_DB = 'RF_Data'
################################################################################################################
class CsvParser:
	def __init__(self, filename):
		self.file = open(filename)
		self.reader = csv.reader(self.file)
		# Get last test ID
		self.current_test = 0

		# Get last File ID
		self.current_file = 0

		# Set up DB Connection
		SQLPWD = getpass.getpass("Database Password: ")
		self.db = MySQLdb.connect(host=SQL_HOST, user=SQL_USER, passwd=SQLPWD, db=SQL_DB)

		self.curs = self.db.cursor()

		# Index Lookup for fields
		self.fieldindex = {}

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.file.close()
		self.db.close()

	# Read First 7-8 lines containing Date, Comment etc.
	def readFileHeader(self):		
		while True:
			row = self.reader.next()
			if len(row) == 0:
				continue
			if row[0] == "Date:":
				self.date = datetime.datetime.strptime(row[1], '%m/%d/%Y %I:%M %p')
				self.date = self.date.strftime('%Y-%m-%d %H:%M')
				
				date = row[1].split("/")
				date[2] = date[2][2:]
				date = "".join(date)
				self.current_file = date.replace(" ", "").replace(":", "")
				
				self.current_file = self.current_file[:len(self.current_file)-2]
			if " Comment:" in row:
				self.comment = row[3]
			if row[0] == "SN":
				self.fieldnames = row
				for i in range(len(self.fieldnames)):
					self.fieldnames[i] = self.fieldnames[i].strip()
					self.fieldindex[self.fieldnames[i]] = i
				break

	# Read through rows and enter into database as appropriate
	def insertToSQL(self):
		print self.fieldnames
		file_entered = 0
		prev_chain = -1	
		for row in self.reader:
			if file_entered == 0:
				self.insertFile(row)
				file_entered = 1

			if prev_chain != row[self.fieldindex["CHAIN"]]:
				self.current_test += 1
				self.insertTestRun(row)

			if "PER" in self.fieldnames:
				self.insertRXPER(row)

			if "Region" in self.fieldnames:
				self.insertSpectrum(row)

			if "Target_Power" in self.fieldnames and "LP_EVM" in self.fieldnames:
				self.insertTXEVM(row)

			if "TXEVM" in self.fieldnames:
				self.insertTXEVMPower(row)

			prev_chain = row[self.fieldindex["CHAIN"]]
	# Insert File entry into File table in SQL Database
	def insertFile(self, row):
		query = """INSERT into File (FileID, SN, Revision, TestType, COMMENT, TESTRUNTIME)
			VALUES ({0}, {1}, {2}, {3}, {4}, {5})
			""".format(self.current_file, repr(row[self.fieldindex["SN"]]), repr(row[self.fieldindex["REVISION"]]), \
				repr(row[self.fieldindex["TestType"]].strip()), repr(self.comment), repr(self.date))

		print query
		self.curs.execute(query)
		self.db.commit()

	# Insert Test Run entry into TestRun table in SQL Database
	def insertTestRun(self, row):
		chan2 = -1
		chans = row[self.fieldindex["CHAN"]].split('p')
		if len(chans) > 1:
			chan2 = chans[1]

		chan1 = chans[0]

		query = """INSERT into TestRun (TestRunID, FileID, CHAIN, BW, CHAN, CHAN_2, BAND, RATE, ANT) 
			VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})
			""".format(self.current_test, self.current_file, row[self.fieldindex["CHAIN"]], \
				repr(row[self.fieldindex["BW"]]), repr(chan1), repr(chan2), \
				repr(row[self.fieldindex["Band"]]), \
				repr(row[self.fieldindex["RATE"]]), repr(row[self.fieldindex["ANT"]]))

		self.curs.execute(query)
		self.db.commit()

	# Insert RXPER entry
	def insertRXPER(self, row):
		query = """INSERT into RXPER (TestRunID, PWR, PER)
			VALUES ({0}, {1}, {2})
			""".format(self.current_test, row[self.fieldindex["PWR"]], row[self.fieldindex["PER"]])

		self.curs.execute(query)
		self.db.commit()

	# Insert TXEVM entry
	def insertTXEVM(self, row):
		query = """INSERT into TXEVM (TestRunID, Target_Power, LP_EVM, LP_Power,
			LP_freqErrorHz, LP_ClockErrorPpm) VALUES ({0}, {1}, {2}, {3}, {4}, {5})
			""".format(self.current_test, row[self.fieldindex["Target_Power"]], \
			row[self.fieldindex["LP_EVM"]], row[self.fieldindex["LP_Power"]], \
			row[self.fieldindex["LP_freqErrorHz"]], row[self.fieldindex["LP_ClockErrorPpm"]])

		self.curs.execute(query)
		self.db.commit()

	# Insert TXEVMPower entry
	def insertTXEVMPower(self, row):
		query = """INSERT into TXEVMPower (TestRunID, FileID, EVM Floor, TXEVM)
			VALUES ({0}, {1}, {2})
			""".format(self.current_test, self.fileID, row[self.fieldindex["EVM Floor"]], row[self.fieldindex["TXEVM"]])

		self.curs.execute(query)
		self.db.commit()

	# Insert Spectrum entry
	def insertSpectrum(self, row):
		passed = 0
		if "PASS" in row[self.fieldindex["Pass/Fail"]]:
			passed = 1

		query = """INSERT into Spectrum (TestRunID, Region, LP_FreqOffset, Mask_Power, Mask_Limit,
			Pass, MARGIN, Fail) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})
			""".format(self.current_test, repr(row[self.fieldindex["Region"]]), \
				row[self.fieldindex["LP_FreqOffset"]], row[self.fieldindex["Mask_Power"]], \
				row[self.fieldindex["Mask_Limit"]], passed, \
				row[self.fieldindex["Margin"]], row[self.fieldindex["Fail(%)"]])

		try:
			self.curs.execute(query)
		except Exception as e:
			print query
 			print e
 			exit()
		self.db.commit()

	# Insert Spectrum Plot entry
	def insertSpectrumPlot(self, row):
		pass
		
with CsvParser(sys.argv[1]) as parser:
	parser.readFileHeader()
	parser.insertToSQL()