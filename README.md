csv_reports
===========

CSVReports

Python module for parsing CSV files into sqlite tables, represented as native python objects, e.g.,
<pre>
>>>
>>> import Reports
>>> foo = Reports.Report('foo.csv')
>>> 
>>> len(foo)
1241
>>> 
>>> foo.sum('price')
Decimal('7412.50')
>>> 
</pre>

Optionally, you can specify a table name and a datbase connection<br />
-- by default, the table name is extracted from the csv file
   and a per-instance in-memory sqlite3 connection will be used.
   In practice you'd only care about these parameters if you want
   a shared db to do joins against multiple reports
<pre>
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
</pre>