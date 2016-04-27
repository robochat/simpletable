#!/usr/bin/env python
"""A very simple table classes written in pure python. It allows us to
index the data either by row index (integer) or by column (text label).
Data is stored by column

The code is inspired by the module tablib but is vastly simplified. For
instance tablib provides automatic validation of insertions etc during 
normal operations and can export and import data to many formats.
"""
from ordereddict import OrderedDict
#from collections import OrderedDict
from collections import Sequence,Mapping,Iterable,Hashable
#import warnings

#TO DO:
#extra methods: slicing by row, insertions, 
#returning OrderedDicts for rows?

class ColTable(object):
    """A very simple table class that supports index and column indexing.
    Stores data by columns."""    
    def __init__(self, items=None, headers=None, title=None, **kwargs):
        """Expects either a dictionary of columnar data, a sequence of 
        row orientated data or a sequence of key,value paths. Even accepts
        keyword arguements (excluding columns named title or headers!)
        Checks that all entries have the same length. 
        
        Input Parameters:
            items -   iterable or mappable object.
            headers - sequence of column names. If provided, this will determine
                      the column ordering.
            title -   sets a name for the dataset.
            kwargs -  extra columns can be provided using keywords. Will be appended
                      to dataset unless colname is in headers or items. Will overwrite
                      entries in items
        """
        self.title = title
        
        if headers and len(set(headers)) != len(headers): 
            raise ValueError("Class doesn't handle columns with duplicate names")
        
        #handle sequence of rows
        if (items and isinstance(items,Iterable)
            #special exception: if the sequence entries are pairs of (Hashable,Iterable) then probably a 'serialised' dict
            and not (isinstance(items[0],Iterable) and len(items[0]) ==2 
                    and isinstance(items[0][0],Hashable) 
                    and isinstance(items[0][1],Iterable)) 
          ): 
            height = len(items)
            widths = (len(row) for row in items)
            width = widths.next()
            if not all(w == width for w in widths): raise ValueError('not all rows have the same number of columns')
            
            if headers:
                datadict = OrderedDict((h,None) for h in headers) #preallocate (not for speed but to get order correct)
                tmpheaders = list(headers)
                for k in kwargs: del tmpheaders[tmpheaders.index(k)] #remove columns that are handled by keyword arguements
                if len(tmpheaders) != width: raise ValueError('headers length does not match length of supplied data')
                if isinstance(items[0],Iterable):
                    for i,h in enumerate(tmpheaders):
                        datadict[h] = [row[i] for row in items]
                elif isinstance(Mapping):
                    for h in tmpheaders:
                        datadict[h] = [row[h] for row in items]
                else:
                    raise TypeError("'%s' object is not handled" %type(items))
                
                #handle the kwargs
                for k,v in kwargs.iteritems():
                    if len(v) != height: raise ValueError('keyword entry (%s) does not match length of dataset' %k)
                    datadict[k] = v
                
            else:
                if isinstance(items[0],Iterable): 
                    raise ValueError('headers sequence needs to be provided for this type of data')
                elif isinstance(items[0],Mapping): #could be dict but could be OrderdDict or similar
                    if len(set(row.keys() for row in items)) != width:  #all entries have the same keys?
                        raise ValueError('not all rows have the same number of columns')
                    tmpheaders = items[0].keys()
                    datadict = OrderedDict()
                    for h in tmpheaders:
                        datadict[h] = [row[h] for row in items]
                    
                    #handle the kwargs
                    for k,v in kwargs.iteritems():
                        if len(v) != height: raise ValueError('keyword entry (%s) does not match length of dataset' %k)
                        datadict[k] = v
                else:
                    raise TypeError("'%s' object is not handled" %type(items))

        else:
            datadict = OrderedDict(items,**kwargs)            
            # Reorder by headers sequence if provided
            if headers:
                if len(headers) != len(datadict):
                    raise ValueError('headers length does not match length of supplied data')
                else:
                    datadict = OrderedDict((h,datadict[h]) for h in headers)

        self.cols= datadict
        self.validate()
        
    def __getitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            if key in self.cols:
                return self.cols[key]
            else:
                raise KeyError
        else:
            return tuple(col[key] for col in self.cols.values())
    
    def __setitem__(self, key, value):
        if isinstance(key, str) or isinstance(key, unicode):
            self.cols[key] = value
            self.validate()
        else:
            if len(value) != len(self.cols): raise ValueError('row update does not have enough columns')
            for col,v in zip(self.cols,value):
                col[key] = v
    
    def __delitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            if key in self.cols:
                del self.cols[key]
            else:
                raise KeyError
        else:
            for h,col in self.cols.iteritems():
                del col[key]
                self.cols[h] = col
                
    def append(self, row):
        """append a row to the table"""
        if len(value) != len(self.cols): raise ValueError('row update does not have enough columns')
        for (key,col),v in zip(self.cols.iteritems(),value):
            #Add code here to handle row types other than list
            col.append(v)
            #self.cols[key] = col

    def __repr__(self):
        try:
            return '<%s table: %s>' % (self.title or 'unnamed',','.join(self.headers))
        except AttributeError:
            return '<table object>'
            
    @property
    def headers(self):
        return self.cols.keys()
        
    def validate(self):
        """checks that all columns have the same length"""
        lengths = [len(c) for c in self.cols.values()]
        length = lengths[0]
        if not all([l == length for l in lengths]): raise AssertionError('Columns do not all have the same length')
        return True
