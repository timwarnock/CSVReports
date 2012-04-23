csv_reports
===========

CSVReports

Python module for parsing CSV files into sqlite tables, represented as native python objects, e.g.,
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
