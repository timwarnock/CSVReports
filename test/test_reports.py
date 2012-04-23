#!/usr/bin/env python
# vim: set tabstop=4 shiftwidth=4 autoindent smartindent:
import os, sys, unittest
from decimal import *

## parent directory
sys.path.insert(0, os.path.join( os.path.dirname(__file__), '..' ))
import Reports

class test_reports(unittest.TestCase):

	def setUp(self):
		self.reports = Reports.Reports('.')

	def tearDown(self):
		self.reports = None

	def test_existing_reports(self):
		self.assertEqual( len(self.reports), 0 )
		self.reports.load('fake_data', 'spam')
		self.assertEqual( len(self.reports), 1 )

	def test_report_info(self):
		fd = self.reports.fake_data
		self.assertTrue('fake_data' in fd.info)

	def test_report_table(self):
		fd = self.reports.fake_data
		self.assertEqual(fd.table, 'fake_data')

	def test_report_headers(self):
		fd = self.reports.fake_data
		self.assertTrue('spam' in fd.headers)
		self.assertTrue('eggs' in fd.headers)

	def test_report_columns(self):
		fd = self.reports.fake_data
		self.assertTrue('spam' in fd.columns)
		self.assertTrue('eggs' in fd.columns)

	def test_report_coded_columns(self):
		s = self.reports.spam_data
		self.assertTrue('c0' in s.columns)
		self.assertTrue('c1' in s.columns)

	def test_report_csv(self):
		fd = self.reports.fake_data
		fd.csv( 'tenlines', fd[0:10] )
		self.assertEqual( len(self.reports.tenlines), 10 )

	def test_reports_gets_coded_columns(self):
		sd = self.reports.spam_data
		foo = sd.gets( {'Spam is Good':'1'} )
		self.assertEqual( foo[0][sd.headers.index('Spam is Good')], '1' )

	def test_report_gets(self):
		fd = self.reports.fake_data
		spam1 = fd.gets( {'spam':'1'} )
		self.assertEqual( spam1[0][0], '1' )

	def test_report_get(self):
		fd = self.reports.fake_data
		spam2 = fd.get( 'spam', '2' )
		self.assertEqual( spam2[0][0], '2' )

	def test_report_sum(self):
		fd = self.reports.fake_data
		eggs = fd.sum( 'eggs', {'spam': '1'} )
		self.assertAlmostEqual(eggs, Decimal(3590.20))

	def test_report_sums(self):
		fd = self.reports.fake_data
		totals = fd.sums( ['spam', 'eggs'], {'spam':'1'} )
		self.assertEquals(totals[0], Decimal(174))
		self.assertAlmostEqual(totals[1], Decimal(3590.20))

	def test_report_db(self):
		f = self.reports.fake_data
		fc = f.db.execute('select count(*) from fake_data').fetchall()[0][0]
		self.assertEqual( fc, len(f) )

if __name__ == '__main__':
	unittest.main()


