import csv
import sys

class CsvParser:
	def __init__(self, filename):
		self.file = open(filename)
		self.reader = csv.reader(self.file)
		self.current_test = 0

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
					self.fieldindex[self.fieldnames[i]] = i
				break

		print self.fieldnames

	# Read through rows and enter into database as appropriate
	def insertToSQL(self):
		prev_chain = -1	
		for row in self.reader:
			if prev_chain != row[self.fieldindex["CHAIN"]]:
				self.current_test += 1
				insertTestRun(row)

	# Insert Test Run entry into TestRun table in SQL Database
	def insertTestRun(self, row):
		pass

	# Insert RXPER entry
	def insertRXPER(self, row):
		pass

	# Insert TXEVM entry
	def insertTXEVM(self, row):
		pass

	# Insert Spectrum entry
	def insertSpectrum(self, row):
		pass

	# Insert Spectrum Plot entry
	def insertSpectrumPlot(self, row):
		pass
		
with CsvParser(sys.argv[1]) as parser:
	parser.readFileHeader()