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
#accept a sequence of column sequences?? how to do this without being too magical?
#lose idea of columns having an order?
#

class ColTable(object):
    """A simple table class that supports index and column indexing.
    Stores data by columns."""    
    def __init__(self, items=[], rowitems=[], headers=[], title='', **kwargs):
        """Expects either a dictionary of columnar data, a sequence of 
        column orientated data or a sequence of (column-name,column-data)
        tuples. Also accepts keyword arguements (excluding columns named
        'items', 'rowitems', 'title' or 'headers'!). Checks that all entries
        have the same length.
        
        Using the rowitems parameter, allows the class to accept row orientated
        data such as a sequence of sequences or mappable items.        
        
        Input Parameters:
            items -   iterable or mappable object. Valid input for a dict or a
                      sequence of columnar data.
            rowitems- iterable row orientated data. (can't use both items and rowitems)
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
        
        if items and rowitems: 
            raise AssertionError("only one of items and rowitems parameters should be used")
        
        elif rowitems: #handle sequence of rows
            height = len(rowitems)
            widths = (len(row) for row in rowitems)
            width = widths.next()
            if not all(w == width for w in widths): raise ValueError('not all rows have the same number of columns')
            
            if headers:
                datadict = OrderedDict((h,None) for h in headers) #preallocate (not for speed but to get order correct)
                tmpheaders = list(headers)
                
                #handle the kwargs
                for k,v in kwargs.iteritems():
                    if len(v) != height: raise ValueError('keyword entry (%s) does not match length of dataset' %k)
                    datadict[k] = v
                    del tmpheaders[tmpheaders.index(k)] #remove columns that are handled by keyword arguements
                
                if len(tmpheaders) != width: raise ValueError('headers length does not match length of supplied data')
                if isinstance(rowitems[0],Iterable):
                    for i,h in enumerate(tmpheaders):
                        datadict[h] = [row[i] for row in rowitems]
                elif isinstance(Mapping):
                    for h in tmpheaders:
                        datadict[h] = [row[h] for row in rowitems]
                else:
                    raise TypeError("'%s' object is not handled" %type(rowitems))

            else:
                if isinstance(rowitems[0],Iterable): 
                    raise ValueError('headers sequence needs to be provided for this type of data')
                elif isinstance(rowitems[0],Mapping): #could be dict but could be OrderdDict or similar
                    if len(set(row.keys() for row in rowitems)) != width:  #all entries have the same keys?
                        raise ValueError('not all rows have the same number of columns')
                    tmpheaders = rowitems[0].keys()
                    datadict = OrderedDict()
                    for h in tmpheaders:
                        datadict[h] = [row[h] for row in rowitems]
                    
                    #handle the kwargs
                    for k,v in kwargs.iteritems():
                        if len(v) != height: raise ValueError('keyword entry (%s) does not match length of dataset' %k)
                        datadict[k] = v
                else:
                    raise TypeError("'%s' object is not handled" %type(items))
        
        #columnar data -  iterable of sequences plus supplied header 
        elif (items and isinstance(items,Iterable) 
                and all(isinstance(item,Iterable) for item in items)
                #special exception: if the sequence entries are pairs of (Hashable,Iterable) then probably a 'serialised' dict
                and not (len(items[0]) ==2 
                        and isinstance(items[0][0],Hashable) 
                        and isinstance(items[0][1],Iterable))
               ):
            if not headers: raise ValueError('headers sequence needs to be provided for this type of data')
            width = len(items)
            heights = (len(col) for col in items)
            height = heights.next()
            if not all(h == height for h in heights): raise ValueError('not all columns have the same number of rows')
            
            datadict = OrderedDict((h,None) for h in headers) #preallocate (not for speed but to get order correct)
            tmpheaders = list(headers)
            
            #handle the kwargs
            for k,v in kwargs.iteritems():
                if len(v) != height: raise ValueError('keyword entry (%s) does not match length of dataset' %k)
                datadict[k] = v
                del tmpheaders[tmpheaders.index(k)] #remove columns that are handled by keyword arguements
            
            if len(tmpheaders) != width: raise ValueError('headers length does not match length of supplied data')
            
            for i,h in enumerate(tmpheaders):
                datadict[h] = items[i]
                
        else: #columnar data - either via items or keywords
            datadict = OrderedDict(items,**kwargs)            
            # Reorder by headers sequence if provided
            if headers:
                if len(datadict) == 0:
                    datadict = OrderedDict((h,[]) for h in headers)
                elif len(headers) != len(datadict):
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
            #could also return the row as an OrderedDict or namedtuple
            return tuple(col[key] for col in self.cols.values())
    
    def __setitem__(self, key, value):
        if isinstance(key, str) or isinstance(key, unicode):
            self.cols[key] = value
            self.validate()
        else:
            if len(value) != len(self.cols): raise ValueError('row update does not have enough columns')
            for col,v in zip(self.cols,value):
                col[key] = v
            #handle assignment of a mappable object?
    
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
        for (key,col),v in zip(self.cols.iteritems(),row):
            #Add code here to handle row types other than list
            col.insert(index,v)
            #self.cols[key] = col
            
    def append(self, row):
        """append a row to the table"""
        if len(row) != len(self.cols): raise ValueError('row update does not have enough columns')
        for (key,col),v in zip(self.cols.iteritems(),row):
            #Add code here to handle row types other than list
            col.append(v)
            #self.cols[key] = col
    
    def extend(self, iterable):
        """extend table by appending rows from the iterable"""
        widths = (len(row) for row in iterable)
        width = widths.next()
        if not all(w == width for w in widths): raise ValueError('not all rows have the same number of columns') 
        if width != len(self.cols): raise ValueError('row insert does not have enough columns')
        for i,((key,col),v) in enumerate(zip(self.cols.iteritems(),iterable)):
            #Add code here to handle row types other than list
            col.extend(index,[row[i] for row in iterable])
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
        if len(self.cols):
            lengths = [len(c) for c in self.cols.values()]
            length = lengths[0]
            if not all([l == length for l in lengths]): raise AssertionError('Columns do not all have the same length')
        return True




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
    """creates a dictionary from sequences of keys and values
    
    headers - a sequence of hashable items
    iterable - a sequence of items (checked to be the same length as headers)
    """
    if len(headers) != len(iterable): raise ValueError('headers amd iterable sequences are not of equal length')
    return dict(zip(headers,iterable))

def rows2dict(headers,iterable):
    """creates a dictionary from sequences of column names and rows of data
    
    headers - a sequence of hashable items
    iterable - a sequence of rows (checked to be all of the same length)
    """
    #checks
    widths = (len(row) for row in iterable)
    width = widths.next()
    if not all(w == width for w in widths): raise ValueError('not all rows have the same number of columns')
    if len(headers) != width: raise ValueError('headers amd dataset are not the same width')
    #
    result = dict((key,[row[i] for row in iterable]) for i,key in enumerate(headers))
    return result
    
