import csv
import sys
import MySQLdb

class CsvParser:
	def __init__(self, filename):
		self.file = open(filename)
		self.reader = csv.reader(self.file)
		# Get last test ID
		self.current_test = 0

		# Get last File ID
		self.current_file = 0

		# Set up DB Connection
		#self.db = MySQLdb.connect(host=SQLHOST, USER=l)

		self.fieldindex = {}

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.file.close()

	# Read First 7-8 lines containing Date, CableLoss etc.
	def readFileHeader(self):		
		while True:
			row = self.reader.next()
			if len(row) == 0:
				continue

			if row[0] == "SN":
				self.fieldnames = row
				for i in range(len(self.fieldnames)):
					self.fieldnames[i] = self.fieldnames[i].strip()
					self.fieldindex[self.fieldnames[i]] = i
				break

		print self.fieldindex

	# Read through rows and enter into database as appropriate
	def insertToSQL(self):
		print self.fieldindex
		prev_chain = -1	
		for row in self.reader:
			if prev_chain != row[self.fieldindex["CHAIN"]]:
				self.current_test += 1
				self.insertTestRun(row)

			if "PER" in self.fieldnames:
				self.insertRXPER(row)

			if "Region" in self.fieldnames:
				self.insertSpectrum(row)

			if "TargetPower" in self.fieldnames:
				self.insertTXEVM(row)

			if "TXEVM" in self.fieldnames:
				self.insertTXEVMPower(row)

			prev_chain = row[self.fieldindex["CHAIN"]]

	# Insert Test Run entry into TestRun table in SQL Database
	def insertTestRun(self, row):
		query = """INSERT into TestRun (TestRunID, FileID, CHAIN, BW, CHAN, BAND, RATE, ANT) 
			VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})
			""".format(self.current_test, self.current_file, row[self.fieldindex["CHAIN"]], \
				row[self.fieldindex["BW"]], row[self.fieldindex["CHAN"]], row[self.fieldindex["Band"]], \
				row[self.fieldindex["RATE"]], row[self.fieldindex["ANT"]])

		print query
	# Insert RXPER entry
	def insertRXPER(self, row):
		query = """INSERT into RXPER (TestRunID, PWR, PER)
			VALUES ({0}, {1}, {2})
			""".format(self.current_test, row[self.fieldindex["PWR"]], row[self.fieldindex["PER"]])

		print query

	# Insert TXEVM entry
	def insertTXEVM(self, row):
		query = """INSERT into TXEVM (TestRunID, TargetPower, LP_EVM, LP_Power,
			LP_freqErrorHz, LP_ClockErrorPpm) VALUES ({0}, {1}, {2}, {3}, {4}, {5})
			""".format(self.current_test, row[self.fieldindex["TargetPower"]], \
			row[self.fieldindex["LP_EVM"]], row[self.fieldindex["LP_Power"]], \
			row[self.fieldindex["LP_freqErrorHz"]], row["LP_ClockErrorPpm"])

		print query

	# Insert TXEVMPower entry
	def insertTXEVMPower(self, row):
		pass
	# Insert Spectrum entry
	def insertSpectrum(self, row):
		pass

	# Insert Spectrum Plot entry
	def insertSpectrumPlot(self, row):
		pass
		
with CsvParser(sys.argv[1]) as parser:
	parser.readFileHeader()
	parser.insertToSQL()