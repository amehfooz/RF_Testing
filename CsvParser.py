import csv
import sys
import getpass
import MySQLdb
import datetime
import argparse

# Turn Off Warnings for MySQL
from warnings import filterwarnings, resetwarnings

filterwarnings('ignore', category = MySQLdb.Warning)


# Uncomment to Turn On Warnings
# resetwarnings()

################################################################################################################
#                                         Database Info                                                        #
################################################################################################################
SQL_HOST = 'localhost'
SQL_USER = 'root'
SQL_DB = 'RF_Data'
################################################################################################################
class CsvParser:
	def __init__(self, filename, passwd):
		self.pwd = ""
		self.fname = filename
		self.file = open(filename)
		self.reader = csv.reader(self.file)
		self.comment = ""
		# Get last test ID
		self.current_test = 0

		# Get last File ID
		self.current_file = 0

		# Set up DB Connection
		SQLPWD = passwd
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
				# Change to SQL Date Format
				self.date = self.date.strftime('%Y-%m-%d %H:%M')
				
				date = row[1].split("/")
				date[2] = date[2][2:]
				date = "".join(date)
				self.current_file = int(self.fname.split("_")[-1].split(".")[0][:-2].replace("-",""))

			if " Comment:" in row:
				self.comment = row[3]
			if row[0] == "SN":
				self.fieldnames = row
				for i in range(len(self.fieldnames)):
					self.fieldnames[i] = self.fieldnames[i].strip().upper()
					self.fieldindex[self.fieldnames[i]] = i
				break

	# Read through rows and enter into database as appropriate
	def insertToSQL(self):
		file_entered = 0
		prev_chain = -1	
		for row in self.reader:
			for i in range(len(row)):
				row[i] = row[i].strip()

			if file_entered == 0:
				self.insertFile(row)
				file_entered = 1

			if prev_chain != row[self.fieldindex["CHAIN"]]:
				self.current_test += 1
				self.insertTestRun(row)

				if "BLOCKER_FREQ(MHZ)" in self.fieldnames:
					self.insertRXBlocker(row)

			if "PER" in self.fieldnames:
				self.insertRXPER(row)

			if "REGION" in self.fieldnames:
				self.insertSpectrum(row)

			if "TARGET_POWER" in self.fieldnames and "LP_EVM" in self.fieldnames:
				self.insertTXEVM(row)

			if "TXEVM" in self.fieldnames:
				self.insertTXEVMPower(row)

			prev_chain = row[self.fieldindex["CHAIN"]]

	# Insert File entry into File table in SQL Database
	def insertFile(self, row):
		query = """INSERT into File (FileID, SN, Station, Revision, TestType, COMMENT, TESTRUNTIME)
			VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6})
			""".format(self.current_file, repr(row[self.fieldindex["SN"]]), repr(row[self.fieldindex["STATION"]]), repr(row[self.fieldindex["REVISION"]]), \
				repr(row[self.fieldindex["TESTTYPE"]].strip()), repr(self.comment), repr(self.date))

		try:
			self.curs.execute(query)
			self.db.commit()
		except Exception as e:
			print e ,"@", query
			exit()

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
				repr(row[self.fieldindex["BAND"]]), \
				repr(row[self.fieldindex["RATE"]]), repr(row[self.fieldindex["ANT"]]))

		try:
			self.curs.execute(query)
			self.db.commit()
		except Exception as e:
			print e ,"@", query
			exit()

	# Insert RXPER entry
	def insertRXPER(self, row):
		query = """INSERT into RXPER (TestRunID, FileID, PWR, PER)
			VALUES ({0}, {1}, {2}, {3})
			""".format(self.current_test, self.current_file, row[self.fieldindex["PWR"]], row[self.fieldindex["PER"]])

		try:
			self.curs.execute(query)
			self.db.commit()
		except Exception as e:
			print e ,"@", query

	# Insert TXEVM entry
	def insertTXEVM(self, row):
		query = """INSERT into TXEVM (TestRunID, FileID, Target_Power, LP_EVM, LP_Power,
			LP_freqErrorHz, LP_ClockErrorPpm) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6})
			""".format(self.current_test, self.current_file, row[self.fieldindex["TARGET_POWER"]], \
			row[self.fieldindex["LP_EVM"]], row[self.fieldindex["LP_POWER"]], \
			row[self.fieldindex["LP_FREQERRORHZ"]], row[self.fieldindex["LP_CLOCKERRORPPM"]])

		try:
			self.curs.execute(query)
			self.db.commit()
		except Exception as e:
			print e ,"@", query

	# Insert TXEVMPower entry
	def insertTXEVMPower(self, row):
		query = """INSERT into TXEVMPower (TestRunID, FileID, EVM Floor, TXEVM)
			VALUES ({0}, {1}, {2}, {3})
			""".format(self.current_test, self.current_file, row[self.fieldindex["EVM FLOOR"]], row[self.fieldindex["TXEVM"]])

		try:
			self.curs.execute(query)
			self.db.commit()
		except Exception as e:
			print e ,"@", query

	# Insert RXBlocker entry
	def insertRXBlocker(self, row):
		query = """INSERT into RXBlocker (TestRunID, FileID, BlockerFreq, BlockerPower, LVL_PWR_Offset)
			VALUES ({0}, {1}, {2}, {3}, {4})
			""".format(self.current_test, self.current_file, row[self.fieldindex["BLOCKER_FREQ(MHZ)"]], \
				row[self.fieldindex["BLOCKER_POWER(DBM)"]], row[self.fieldindex["BLOCKER_LVLPWROFFSET(DB)"]])

		try:
			self.curs.execute(query)
			self.db.commit()
		except Exception as e:
			print e ,"@", query

	# Insert Spectrum entry
	def insertSpectrum(self, row):
		passed = 0
		if "PASS" in row[self.fieldindex["PASS/FAIL"]]:
			passed = 1

		query = """INSERT into Spectrum (TestRunID, FileId, Region, LP_FreqOffset, Mask_Power, Mask_Limit,
			Pass, MARGIN, Fail) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})
			""".format(self.current_test, self.current_file, repr(row[self.fieldindex["REGION"]]), \
				row[self.fieldindex["LP_FREQOFFSET"]], row[self.fieldindex["MASK_POWER"]], \
				row[self.fieldindex["MASK_LIMIT"]], passed, \
				row[self.fieldindex["MARGIN"]], row[self.fieldindex["FAIL(%)"]])

		try:
			self.curs.execute(query)
			self.db.commit()
		except Exception as e:
			print e ,"@", query

	# Insert Spectrum Plot entry
	def insertSpectrumPlot(self, row):
		pass

# Setup Argument Parser

parser = argparse.ArgumentParser()
parser.add_argument('CSV', type=str, nargs='+', help='Enter CSV File Name')
parser.add_argument('-p', type=str, help='Password for SQL Database')

args = parser.parse_args()

with CsvParser(" ".join(args.CSV), args.p) as parser:
	parser.readFileHeader()
	parser.insertToSQL()