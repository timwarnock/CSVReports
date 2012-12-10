#!/usr/bin/env python
# vim: set tabstop=4 shiftwidth=4 autoindent smartindent:
import logging, os, sys, unittest
from decimal import *

## parent directory
sys.path.insert(0, os.path.join( os.path.dirname(__file__), '..' ))
import Reports

## set logging level
#logging.getLogger().setLevel(logging.DEBUG)

class test_reports(unittest.TestCase):

	def setUp(self):
		self.reports = Reports.Reports('.')

	def tearDown(self):
		self.reports.db.close()
		del self.reports
		if os.path.exists('temp_data._.csv'):
			os.unlink('temp_data._.csv')

	def test_existing_reports(self):
		self.assertEqual( len(self.reports), 0 )
		self.reports.load('fake_data', 'spam')
		self.assertEqual( len(self.reports), 1 )

	def test_iter_reports(self):
		self.reports.fake_data
		self.reports.spam_data
		iter_reports = []
		for x in self.reports:
			iter_reports.append(x)
		self.assertTrue('fake_data' in iter_reports)
		self.assertTrue('spam_data' in iter_reports)

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

	def test_report_slice(self):
		f = self.reports.fake_data
		f.csv('temp_data', f[0:100:10])
		self.assertEqual( len(self.reports.temp_data), 10 )

	def test_report_slice_10(self):
		f = self.reports.fake_data
		f.csv('temp_data', f[0:100:10])
		t = self.reports.temp_data
		self.assertEqual( len(t), 10 )
		self.assertEqual( t[0], f[0] )
		self.assertEqual( t[1], f[10] )
		self.assertEqual( t[2], f[20] )
		self.assertEqual( t[9], f[90] )

	def test_report_slice_7(self):
		f = self.reports.fake_data
		f.csv('temp_data', f[3:100:7])
		t = self.reports.temp_data
		self.assertEqual( len(t), 14 )
		self.assertEqual( t[0], f[3] )
		self.assertEqual( t[1], f[10] )
		self.assertEqual( t[2], f[17] )
		self.assertEqual( t[12], f[87] )
		self.assertEqual( t[13], f[94] )

	def test_report_slice_77(self):
		f = self.reports.fake_data
		f.csv('temp_data', f[103:200:7])
		t = self.reports.temp_data
		self.assertEqual( len(t), 14 )
		self.assertEqual( t[0], f[103] )
		self.assertEqual( t[1], f[110] )
		self.assertEqual( t[2], f[117] )
		self.assertEqual( t[12], f[187] )
		self.assertEqual( t[13], f[194] )

	def test_report_csv(self):
		fd = self.reports.fake_data
		fd.csv('temp_data', fd[0:10])
		self.assertEqual( len(self.reports.temp_data), 10 )

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


