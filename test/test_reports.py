#!/usr/bin/env python
# vim: set tabstop=4 shiftwidth=4 autoindent smartindent:
import os, sys, unittest
from decimal import *

## parent directory
sys.path.insert(0, os.path.join( os.path.dirname(__file__), '..' ))
import Reports

class test_reports(unittest.TestCase):

	def setUp(self):
		self.reports = sartre.reporting.reports('_FAKE_EXTRACT')

	def tearDown(self):
		self.reports = None

	def test_existing_reports(self):
		self.assertEqual( len(self.reports), 0 )
		self.reports.load('transaction_count')
		self.reports.load('transaction_detail', 'id')
		self.assertEqual( len(self.reports), 2 )

	def test_report_asof(self):
		c = self.reports.transaction_count
		self.assertEqual(c.asof, '2012-04-15 00:00:00')

	def test_report_vendor(self):
		c = self.reports.transaction_count
		self.assertEqual(c.vendor, 'NYT')

	def test_report_fp(self):
		c = self.reports.transaction_count
		self.assertEqual(c.fp, '201204')

	def test_report_info(self):
		c = self.reports.transaction_count
		self.assertTrue('transaction_count' in c.info)

	def test_report_table(self):
		c = self.reports.transaction_count
		self.assertEqual(c.table, 'transaction_count')

	def test_report_headers(self):
		c = self.reports.transaction_count
		self.assertTrue('created' in c.headers)
		self.assertTrue('captured' in c.headers)
		self.assertTrue('settled' in c.headers)
		self.assertTrue('chargeback' in c.headers)
		self.assertTrue('failed' in c.headers)

	def test_report_columns(self):
		c = self.reports.transaction_count
		self.assertTrue('created' in c.columns)
		self.assertTrue('captured' in c.columns)
		self.assertTrue('settled' in c.columns)
		self.assertTrue('chargeback' in c.columns)
		self.assertTrue('failed' in c.columns)

	def test_report_coded_columns(self):
		c = self.reports.transaction_coded_column_count
		self.assertTrue('c0' in c.columns)
		self.assertTrue('c4' in c.columns)

	def test_report_csv(self):
		td = self.reports.transaction_detail
		td.csv( 'tenlines', td[0:10] )
		self.assertEqual( len(self.reports.tenlines), 10 )

	def test_reports_gets_coded_columns(self):
		c = self.reports.transaction_coded_column_count
		foo = c.gets( {'Created Transactions':'300'} )
		self.assertEqual( foo[0][c.headers.index('Created Transactions')], '300' )

	def test_report_gets(self):
		td = self.reports.transaction_detail
		purchases = td.gets( {'create_period':td.fp, 't_type':'PURCHASE'} )
		self.assertEqual( len(purchases), 298 )

	def test_report_get(self):
		td = self.reports.transaction_detail
		notax = td.get( 'tax', '0' )
		self.assertEqual( len(notax), 825 )

	def test_report_sum(self):
		td = self.reports.transaction_detail
		purchase = td.sum( 'purchase', {'create_period':td.fp, 't_type':'PURCHASE'} )
		self.assertAlmostEqual(purchase, Decimal(4829.67))

	def test_report_sums(self):
		td = self.reports.transaction_detail
		totals = td.sums( ['amount', 'price', 'purchase', 'discount', 'tax'], {'create_period':td.fp, 't_type':'PURCHASE'} )
		self.assertAlmostEqual(totals[0], Decimal(4829.67))
		self.assertAlmostEqual(totals[1], Decimal(191.869962))
		self.assertAlmostEqual(totals[2], Decimal(4829.67))
		self.assertAlmostEqual(totals[3], Decimal(2058.54))
		self.assertAlmostEqual(totals[4], Decimal(54.81))

	def test_report_db(self):
		td = self.reports.transaction_detail
		tdc = td.db.execute('select count(*) from transaction_detail').fetchall()[0][0]
		self.assertEqual( tdc, len(td) )

if __name__ == '__main__':
	unittest.main()


