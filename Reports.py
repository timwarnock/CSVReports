import csv, glob, re, os, sys
import collections, codecs
import sqlite3
from decimal import Decimal

## set the logging level
import logging
logging.basicConfig(
  format='%(levelname)s:%(filename)s:%(lineno)d -- %(message)s'
)

def isfloat(s):
	try:
		float(s)
		return True
	except:
		return False

def write_csv(filename, data, headers, info):
	'''
	write a custom csv file (that can be ingested as a Report object if needed)
	'''
	logging.debug('saving %s' % (filename))
	fh = codecs.open(filename, 'w', encoding='utf-8')
	_csv = lambda raw: fh.write(u','.join(['"%s"'%(str(x).decode('utf-8', 'ignore')) for x in raw]) + u'\n')
	_csv(info)
	_csv(headers)
	for row in data:
		_csv(row)
	fh.close()


class Report(collections.Mapping):
	'''
	Interface into a csv report

	In the simplest form, pass in the file you want to parse
	>>> 
	>>> billing_detail = Report('billing-detail.csv')
	>>> billing_detail.sum('Tax Amount')
	Decimal('103796.1')
	>>> 
	>>> len(billing_detail)
	319133
	>>> 

	Optionally, you can specify a table name and a datbase connection
	-- by default, the table name is extracted from the csv file
	   and a per-instance in-memory sqlite3 connection will be used.
	   In practice you'd only care about these parameters if you want
	   a shared db to do joins against multiple reports
	>>> 
	>>> conn = sqlite3.connect(':memory:')
	>>> sales_tax = Report('sales-tax.csv', 'sales_tax', conn)
	>>> billing_summary = Report('billing-summary.csv', 'billing_summary', conn)
	>>> 
	>>> # We should have both tables (sales_tax and billing_summary)
	>>> curs = conn.cursor()
	>>> curs.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
	[(u'sales_tax',), (u'billing_summary',)]
	>>> 
	'''

	def __init__(self, filehint, table = None, conn = None):
		self.filename = Reports.find_report(filehint)
		self.info = []
		self.asof = ''
		self.fp = ''
		self.vendor = ''
		self.headers = []
		self.columns = []
		self.table = table
		self.db = conn
		if conn is None:
			self.db = sqlite3.connect(':memory:')
		self.db.text_factory = str
		self.indexes = []
		self._load_csv()

	def _load_csv(self):
		logging.debug('loading %s' %(self.filename))
		curs = self.db.cursor()
		fh = open(self.filename, 'U')
		def nonull(stream):
			for line in stream:
				yield line.replace('\x00', '')
		reader = csv.reader(nonull(fh))

		# get report metadata
		self.info = reader.next()
		self.asof = self._info('asof')
		self.fp = self._info('fp')
		self.vendor = self._info('vendor')
		self.headers = reader.next()
		if not self.table:
			self.table = self._info('Report').replace('.', '_').replace('-', '_')

		# set the columns (use coded names if there are ANY non-alphanumeric headers)
		if re.search('[\W]', ''.join( self.headers )):
			self.columns = ['c'+str(x) for x in range(len(self.headers))]
		else:
			self.columns = self.headers
		columnTypes = ' TEXT, '.join( self.columns ) + ' TEXT'

		# create the table and load data
		try:
			curs.execute('CREATE TABLE %s(%s)' %(self.table, columnTypes))
		except sqlite3.OperationalError as e:
			logging.debug('%s -- using existing table' %(e))
		else:
			curs.executemany('INSERT INTO %s (%s) VALUES(%s)' %(
				self.table, 
				','.join(self.columns),
				'?, ' * (len(self.headers) -1) + '?'
			), reader)
			self.db.commit()
		curs.close()

	def _info(self, key):
		if key in self.info and len(self.info) > self.info.index(key)+1:
			return self.info[ self.info.index(key) + 1 ]

	def _column(self, key):
		if key.lower() not in [x.lower() for x in self.headers]:
			raise IndexError('%s not in %s'%(key, self.table))
		return self.columns[ [x.lower() for x in self.headers].index(key.lower()) ]

	def create_index(self, col):
		col = self._column(col)
		icol = 'i' + col
		if icol not in self.indexes:
			logging.debug('adding index %s to %s(%s)' %(icol, self.table, col))
			curs = self.db.cursor()
			curs.execute('CREATE INDEX IF NOT EXISTS %s ON %s(%s)' %(icol, self.table, col))
			curs.close()
			self.indexes.append(icol)

	def __getitem__(self, key):
		curs = self.db.cursor()
		if isinstance( key, slice ):
			start = 0 if key.start is None else key.start
			stop = len(self) - key.start if key.stop is None else key.stop
			qstep = ''
			if key.step is not None:
				qstep = ' AND ROWID %% %s = %s ' %(key.step, (start+1) % key.step)
			res = curs.execute('SELECT * FROM %s WHERE ROWID > %s AND ROWID <= %s %s' 
				%(self.table, start, stop, qstep)).fetchall()
		else:
			res = list(curs.execute('SELECT * FROM %s WHERE ROWID = %s' %(self.table, key+1)).fetchall()[0])
		curs.close()
		return res 

	def __iter__(self):
		curs = self.db.cursor()
		self.__iter = curs.execute('SELECT * FROM %s' %(self.table))
		curs.close()
		return self

	def next(self):
		return self.__iter.next()

	def __len__(self):
		curs = self.db.cursor()
		ret = curs.execute('SELECT COUNT(*) FROM %s' %(self.table)).fetchall()[0][0]
		curs.close()
		return ret

	def get(self, column, value):
		'''
		get rows where column matches value

		>>> billing_detail = Report('billing-detail.csv')
		>>> billing_detail.get('Transaction Id', '5775423')
		'''
		curs = self.db.cursor()
		column = self._column(column)
		ret = curs.execute("SELECT * FROM %s WHERE %s = '%s'" %(self.table, column, value)).fetchall()
		curs.close()
		return ret

	def gets(self, filter = {}):
		'''
		get filtered rows

		>>> billing_detail = Report('billing-detail.csv')
		>>> billing_detail.gets({'Tax Amount':0, 'Quantity':2})
		'''
		curs = self.db.cursor()
		_where = []
		for k,v in filter.iteritems():
			_where.append(" %s = '%s' " %(self._column(k),v) )
		ret = curs.execute('SELECT * FROM %s %s' %(
			self.table,
			' WHERE ' + ' AND '.join(_where) if _where else ''
			)).fetchall()
		curs.close()
		return ret

	def sum(self, col, filter = {}):
		'''
		return the sum of all values in the selected column
		
		Optionally, an additional where clause can be added using the filter option, e.g.,
		>>> 
		>>> revenue_recog.sum('Gross Deferred', {'Fiscal Period':'2011-09'})
		Decimal('3307750.14197')
		>>> 
		'''
		return self.sums([col], filter)[0]

	def sums(self, cols, filter = {}):
		'''
		Similar to sum() except returns a list of multiple sums
		'''
		curs = self.db.cursor()
		_where = []
		for k,v in filter.iteritems():
			_where.append(" %s = '%s' " %(self._column(k),v) )
		ret = curs.execute('SELECT %s FROM %s %s' %(
			','.join(['SUM(COALESCE(%s,0))'%(self._column(col)) for col in cols]),
			self.table,
			' WHERE ' + ' AND '.join(_where) if _where else ''
			)).fetchall()[0]
		curs.close()
		return [Decimal(str(x)) if isfloat(x) else Decimal('0') for x in ret]

	def csv(self, title, data=None):
		''' output a csv into the same directory as this Report using the same headers and info metadata
		'''
		if data is None:
			curs = self.db.cursor()
			data = curs.execute('SELECT * FROM %s' %(self.table)).fetchall()
			curs.close()
		filename = os.path.join( os.path.dirname(self.filename), '%s._.csv' % (title))
		write_csv(filename, data, self.headers, self.info)



class Reports:
	'''
	Magic collection of reports

	Maintains a single shared database of all reports, lazily loaded
	as needed, where the table name is the same as attribute name.

	Optionally, a database can be provided, otherwise a per-instance
	in-memory sqlite3 database will be used.

	>>> reports = Analyzer.Reports('/home/user/reports-1109')
	>>> reports.billing_detail.sum('Tax Amount')
	Decimal('103796.1')
	>>> 
	>>> curs = reports.conn.cursor()
	>>> curs.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
	[(u'billing_detail',)]
	>>> 
	>>> reports.billing_summary.sum('Tax Amount')
	Decimal('103796.1')
	>>> 
	>>> curs.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
	[(u'billing_detail',), (u'billing_summary',)]
	>>> 
	'''

	def __init__(self, reportdir = '.', conn = None):
		self.reports = {}
		self.reportdir = reportdir
		self.db = conn
		if conn is None:
			self.db = sqlite3.connect(':memory:')

	def __len__(self):
		return len(self.reports)

	def __getattr__(self, report):
		'''
		magically find reports within self.reportdir

		For example, if there is a report 'sales-tax.2011-09._._.20111018152657.csv'
		You can access this with an attribute 'sales_tax', e.g.,
		>>> 
		>>> reports = Reports()
		>>> len(reports.sales_tax)
		4884
		>>> reports.sales_tax.info
		['Report', 'sales_tax.summary-20111018', 'Fiscal Period', '23714', 'Vendor', 'NYT']
		>>> 
		'''
		if report.startswith('__'):
			raise AttributeError
		else:
			return self.load(report)

	def load(self, report, index = None):
		'''load a report by name, with optional index
		'''
		filename = Reports.find_report(self.reportdir, report.replace('_', '?') + '.*csv')
		if filename is None or not os.stat(filename):
			return None
		if report not in self.reports:
			self.reports[report] = Report(filename, table=report, conn=self.db)
			if index:
				self.reports[report].create_index(index)
		return self.reports[report]
		
	def csv(self, title, data, headers, info):
		''' output a csv file into this "Reports" directory
		'''
		filename = os.path.join(self.reportdir, '%s._.csv' % (title))
		write_csv(filename, data, headers, info)

	@classmethod
	def find_report(self, *hints):
		files = glob.glob( os.path.join(*hints) )
		if len(files) == 1:
			return files[0]
		elif len(files) == 0:
			logging.error('No reports found: find_report(%s)' %(os.path.join(*hints)))
		else:
			logging.error('Found too many matching reports: find_report(%s) => %s' %(os.path.join(*hints), ', '.join(files) ))


