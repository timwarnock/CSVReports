CSVReports
===========

Python module for parsing CSV files into sqlite tables, represented as native python objects, e.g.,
<pre>
>>>
>>> import Reports
>>> foo = Reports.Report('foo.csv')
>>> 
>>> len(foo)
1241
>>> 
>>> foo.headers
['id', 'price', 'description']
>>>
>>> foo.sum('price')
Decimal('7412.50')
>>> 
>>> everyother = foo[0:100:2]
>>> len(everyother)
50
>>>
</pre>

A Reports class provides a collection of reports, and uses the same sqlite connection (to allow joins across reports).
In other words, all of the csv reports will be viewed as tables within a single database, and all reports can be
accessed by named attributes. E.g.,
<pre>
>>>
>>> reports = Reports.Reports('/path/to/reports')
>>> 
>>> reports.billing_detail.sum('Tax Amount')
Decimal('103796.1')
>>> 
>>> reports.tax_detail.sum('Amount')
Decimal('103796.1')
>>> 
>>> taxes = reports.db.execute('SELECT b.id, b.price, t.amount FROM billing_detail b, tax_detail t WHERE t.billing_id = b.id').fetchall()
>>> len(taxes)
2549
>>> 
</pre>

Optionally, you can specify a table name and a database connection<br />
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
