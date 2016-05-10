#!/usr/bin/env python
"""A simple table classes written in pure python. It allows us to
index the data either by row index (integer) or by column (text label).
Data is stored by column

This class inherits from an OrderedDict
"""
from ordereddict import OrderedDict
#from collections import OrderedDict
from collections import Sequence,Mapping,Iterable,Hashable
#import warnings

#TO DO
# class should be able to handle mappable objects (dict-types) for set, append, insert, extend
# handle seting values by slice properly
# iter by row
# 

class ColTable(object):
    """A simple table class that supports index and column indexing.
    Stores data by columns."""    
    def __init__(self, *args, **kwargs):
        """Takes the same input as a dict type but each value should be a
        sequence of the same length.
        """
        self.cols = OrderedDict(*args,**kwargs)
        self.validate()
    
    @property
    def headers(self):
        return self.cols.keys()
        
    def __repr__(self):
        try:
            return '<%s table: %s>' % (self.title or 'unnamed',','.join(self.headers))
        except AttributeError:
            return '<table object>'
        
    def validate(self):
        """checks that all columns have the same length"""
        if len(self.cols):
            try:
                lengths = [len(c) for c in self.cols.values()]                
            except TypeError as e:
                raise TypeError('not all columns have a len()')
            length = lengths[0]
            if not all([l == length for l in lengths]): raise AssertionError('Columns do not all have the same length')
        return True

    def __getitem__(self, key):
        if isinstance(key, int): 
            return OrderedDict((name,col[key]) for name,col in self.cols.items())
        elif isinstance(key, slice): #return another instance of class
            return ColTable((name,col[key]) for name,col in self.cols.items())
        else:
            try:
                return self.cols[key]
            except ValueError:
                raise KeyError('column does not exist')            
    
    def __setitem__(self, key, value):
        if isinstance(key, int):
            if len(value) != len(self.cols): raise ValueError('row update does not have enough columns')
            for col,v in zip(self.cols,value):
                col[key] = v
            #handle assignment of a mappable object?        
        elif isinstance(key, slice):
            width = len(self.cols)
            if not all(len(row) == width for row in value): raise ValueError('(some of) rows update do not have enough columns')
            indices = range(*key.indices(len(self)))
            for key,row in zip(indices,value):
                for col,v in zip(self.cols,row):
                    col[key] = v
        else:
            self.cols[key] = value
            self.validate()
    
    def __delitem__(self, key):
        if not (isinstance(key, int) or isinstance(key, slice)):
            try:
                del self.cols[key]
            except ValueError:
                raise KeyError('column does not exist')
        else:
            for h,col in self.cols.iteritems():
                del col[key]
                self.cols[h] = col
    
    def __iter__(self):
        """iterate over the rows rather than the columns (can always access the cols
        attribute directly)."""
        for i in range(len(self)):
            #return dict((name,col[i]) for name,col in self.cols.items())
            #return tuple(col[i] for col in self.cols.values())
            #namedtuple?
            #return list(col[i] for col in self.cols.values())
            return OrderedDict((name,col[i]) for name,col in self.cols.items())
        
    def __len__(self):
        """number of rows in the dataset"""
        return len(self.cols.values()[0]) #assuming that collection is self-consistant
        
    def select(self,headers):
        """retrieve only selected columns from the dataset. Data is returned as another
        ColTable class.
        
        headers - iterable of columns to return, requested ordering is preserved"""
        return ColTable((key,self.col[key]) for key in headers)        
        
    def insertcol(self,index,key,value):
        """inserted a column of data before index"""
        #need to create a new OrderedDict
        headers = self.headers
        headers.insert(index, key)
        self[key] = value # append new column onto end
        newdict = OrderedDict((h,datadict[h]) for h in headers)
        self.cols = newdict #replace current cols OrderedDict with new one.
    
    def insert(self, index, row):
        """insert row before index"""
        if len(row) != len(self.cols): raise ValueError('row insert does not have enough columns')
        if isinstance(row,Mappable):
            for key,col in self.cols.iteritems():
                #Add code here to handle row types other than list
                col.insert(index,row[key])
                #self.cols[key] = col            
        else:
            for (key,col),v in zip(self.cols.iteritems(),row):
                #Add code here to handle row types other than list
                col.insert(index,v)
                #self.cols[key] = col
            
    def append(self, row):
        """append a row to the table"""
        if len(row) != len(self.cols): raise ValueError('appended row does not have enough columns')
        if isinstance(row,Mappable):
            for key,col in self.cols.iteritems():
                #Add code here to handle row types other than list
                col.append(row[key])
                #self.cols[key] = col            
        else:
            for (key,col),v in zip(self.cols.iteritems(),row):
                #Add code here to handle row types other than list
                col.append(v)
                #self.cols[key] = col
    
    ??def extend(self, iterable):
        """extend table by appending rows from the iterable"""
        widths = (len(row) for row in iterable) #using up iterable!!!
        width = widths.next()
        if not all(w == width for w in widths): raise ValueError('not all rows have the same number of columns') 
        if width != len(self.cols): raise ValueError('row insert does not have enough columns')
        if isinstance(iterable,Mappable):
            for key,col in self.cols.iteritems():
                #Add code here to handle row types other than list
                col.extend(row[key] for row in iterable)
                #self.cols[key] = col            
        else:            
            for i,(key,col) in enumerate(self.cols.iteritems()):
                #Add code here to handle row types other than list
                col.extend([row[i] for row in iterable])
                #self.cols[key] = col



def rows2cols(iterable):
    """takes an iterable of row sequences and returns a list of lists of
    columnar data."""
    #checks
    widths = (len(row) for row in iterable)
    width = widths.next()
    if not all(w == width for w in widths): raise ValueError('not all rows have the same number of columns')
    #
    result = [[row[i] for row in iterable] for i in range(width)]
    return result

def cols2dict(headers,iterable):
    """creates an ordered dictionary from sequences of keys and values
    
    headers - a sequence of hashable items
    iterable - a sequence of items (checked to be the same length as headers)
    """
    if len(headers) != len(iterable): raise ValueError('headers amd iterable sequences are not of equal length')
    return OrderedDict(zip(headers,iterable))

def rows2dict(headers,iterable):
    """creates an ordered dictionary from sequences of column names and rows of data
    
    headers - a sequence of hashable items
    iterable - a sequence of rows (checked to be all of the same length)
    """
    #checks
    widths = (len(row) for row in iterable)
    width = widths.next()
    if not all(w == width for w in widths): raise ValueError('not all rows have the same number of columns')
    if len(headers) != width: raise ValueError('headers amd dataset are not the same width')
    #
    result = OrderedDict((key,[row[i] for row in iterable]) for i,key in enumerate(headers))
    return result
    
