simpletable - a simple table datastructure
==========================================

Introduction
------------

Simpletable is a tiny datastructure library for python2 (not python3 currently)
that provides two versions of a table class i.e. a way of storing data in rows
and columns.

simpletable consists of two classes - `Table` and `ColTable` which can be used to
store a regular array of data. This data can then be indexed using an integer to
access each row or by column name/key to access the columns. Methods exist to add
more rows or columns; the classes check that the new data has the appropriate
number of rows or columns, otherwise an exception is thrown.

The `Table` class inherits from a list and so mostly acts like a list except for
it's extended indexing abilities, data is stored by row. The `ColTable` class 
uses an OrderedDict internally and stores data by column. 

The classes expect the data to be stored in lists and their methods for updating 
the dataset depend upon this but it is not enforced, this allows the user to use 
the datastructures as they see fit. For instance, each column is likely to have 
a single data type and so columns might be stored as numpy arrays in a `ColTable`
(except that the methods insert(), append() and pop() will then not work).

Usage
-----

The `Table` class takes anything acceptable to a list class except that each
item must have a length and all must have the same length.

```python
data = [[1, 'red', 13.0],
        [2, 'blue', 15.0],
        [3, 'green', 2.0],
        [4, 'orange', -12.0],
        [5, 'yellow', 0.0]]
     
ds = Table(data, headers = ['idx', 'colour', 'value'], title = 'example')
# Nb. headers and title must be entered as keywords

ds[0]
> [1, 'red', 13.0]
ds['colour']
> ['red','blue','green','orange','yellow']
ds[0:3] # slicing creates a new table instance

ds2 = Table()
ds2.headers = ['name','surname']
ds2.append(['Dave','Brubeck'])
ds2.append(['Charlie','Parker'])
ds2.insert(0,['Miles','Davies'])
```

The table classes also accept assignments either by row or column as long as
the new entry is compatible with the data shape. New columns (but not new rows)
can also be created by assignment. Rows and columns can be deleted as might be
expected.

In addition to a normal list's methods, there are the new methods `insertcol()`
and `validate()` as well as the properties `width` and `headers`.

The `ColTable` class takes anything acceptable to an OrderedDict class
except that each item must have a length and all must have the same length.

```python
data = (('idx',[1,2,3,4,5]),
        ('colour',['red','blue','green','orange','yellow']),
        ('value',[13.0, 15.0, 2.0, -12.0, 0.0]))

ds3 = ColTable(data)
ds3[0]
> [1, 'red', 13.0]
ds['colour']
> ['red','blue','green','orange','yellow']
ds[0:3] # slicing creates a new table instance      
```

The underlying OrderedDict can be accessed via the `cols` attribute without
any concerns about corrupting the `ColTable` instance. It adds some methods
that allow it to be treated more like a list - `append()`,`insert()`,`pop()`.
In addition it has the methods `insertcol()` and `select()` and the properties
`width` and `headers`.

But the code is very short and can be easily inspected if anything is unclear.


Alternatives
------------

Now, I'm going to discuss why you might not actually want to use these classes. 
Although, they are very light-weight and ameniable to adaption, they are not
optimal for handling lots of data or complicated queries, neither do they have 
the functionality of other libraries. Finally they not offer ways to persist data.

Other libraries already exist that offer similar functionality. The most similar
being [tablib](https://github.com/kennethreitz/tablib) which is often recommended 
and is very similar to the module simpletable but offers additional functionality, 
particularly for transforming the data into and from different types such as xls, csv,
json, yaml. Another similar library is [eztable](http://pythonhosted.org/eztable). 
Many other packages (such as [sqlalchemy](http://www.sqlalchemy.org)) avoid 
 datastructures like this and return data as a list of namedtuples or dicts or 
special Row class instances.

If more functionality is required, then [pandas](http://pandas.pydata.org/) is a 
heavy-weight library which can certainly do anything that you are likely to need 
although there is a slight learning curve. Many other libraries shared this space 
a few years ago ([petl links](http://petl.readthedocs.io/en/latest/related_work.html))
but pandas has become the defacto winner (as of 2016). 

An alternative to Pandas (although it can be used by Pandas) suitable for storing
lots of data is [pytable](http://www.pytables.org) which is a python library built 
around HDF5 files.

Last but not least, a relational database might be just what you're looking for since
storing tables of data efficiently is exactly what they do. In the context of this
library, a [sqlite](https://docs.python.org/2/library/sqlite3.html) in-memory database
 instance will provide more efficient storage and advanced queries. There are even 
 pure python database packages such as [tinydb](https://pypi.python.org/pypi/tinydb)

Columnar storage of table data is also popular in the database world although like the
ColTable class, it is not always apparent, see [bcolz](http://bcolz.blosc.org) or 
maybe in the future [feather]( https://github.com/wesm/feather).
