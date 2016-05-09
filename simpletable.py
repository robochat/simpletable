#!/usr/bin/env python
"""A very simple table classes written in pure python. It allows us to
index the data either by row index (integer) or by column (text label).

The code is inspired by the module tablib but is simplified. For
instance tablib provides automatic validation of insertions etc during 
normal operations and can export and import data to many formats.
"""

class Table(list):
    """A very simple table class that supports index and column indexing.
    
    Column names should be strings (or unicode). The class also doesn't 
    cope well with duplicate column names, so best to avoid that.
        
    The class doesn't change the type of the row entries given to it. 
    Hence if immutable row entries are inserted then it won't be possible
    to append or change entries by column indexing later.
    
    The list method extend() is not currently validated.
    """
    def __init__(self, *args, **kwargs):
        """Takes an iterable. Can also use the keyword argument 'headers' to 
        set the column headers.      
        """        
        list.__init__(self, *args)
        self.title = kwargs.pop('title',None)
        self._headers = list(kwargs.pop('headers',[]))
        
        if len(set(self._headers)) != len(self._headers): 
            raise ValueError("Class doesn't handle columns with duplicate names")
        
        if kwargs: raise TypeError('got an unexpected keyword argument %s',kwargs.pop())
        self.validate()
        
    def __getitem__(self, key):
        if not isinstance(key, int):
            try:
                pos = self._headers.index(key) # get 'key' index from each data
                return [row[pos] for row in self]
            except ValueError as e:
                raise KeyError('column does not exist')
        else:
            #could also return the row as an OrderedDict or namedtuple?
            return super(Table,self).__getitem__(key)
    
    def __setitem__(self, key, value):
        if not isinstance(key, int):
            if len(value) != len(self):
                raise ValueError('new column %s is not the correct length for dataset' %str(key))
            if key in self._headers:
                pos = self._headers.index(key)
                for i,(row,val) in enumerate(zip(self,value)):
                    row[pos] = val
                    #super(Table,self).__setitem__(i,row)
            else:
                self._headers.append(key)
                for i,(row,val) in enumerate(zip(self,value)):
                    row += [val]
                    #row.append(val)
                    #super(Table,self).__setitem__(i,row)
        else:
            if len(value) != self.width: raise ValueError('new row is not the correct width for the dataset')
            super(Table,self).__setitem__(key,value)
    
    def __delitem__(self, key):
        if not isinstance(key, int):
            try:
                pos = self.headers.index(key)
                del self.headers[pos]
                for i, row in enumerate(self):
                    del row[pos]
                    self[i] = row
            except ValueError as e:
                raise KeyError('column does not exist')
        else:
            super(Table,self).__delitem__(key)
            
    def insertcol(self,index,key,value):
        """inserted a column of data before index"""
        if len(value) != len(self):
            raise ValueError('new column %s is not the correct length for dataset' %str(key))
        self._headers.insert(index,key)
        for i,(row,val) in enumerate(zip(self,value)):
            row.insert(index,val)
            #row.append(val)
            #super(Table,self).__setitem__(i,row)
        #self.validate()

    def __repr__(self):
        try:
            return '<%s table: %s: %d entries>' % (self.title or 'unnamed',','.join(self.headers),len(self))
        except AttributeError:
            return '<table object>'
            
    @property
    def width(self):
        return len(self[0]) if len(self) else len(self.headers)
    
    @property
    def headers(self):
        # since headers simply returns _headers list, internal methods often refer to _headers directly
        return self._headers
        
    @headers.setter
    def headers(self,newheaders):
        width = self.width
        if width and len(newheaders) != width: raise ValueError('new header is not the correct length for dataset')
        self._headers = newheaders
        
    def append(self,obj):
        """L.append(object) -- append row to end"""
        width = self.width
        if width and len(obj) != width: raise ValueError('new row is not the correct length for dataset: %r' %obj)
        super(Table,self).append(obj)
        
    def validate(self):
        """checks that all rows have the same length"""
        width = self.width
        if len(self.headers) != width: raise AssertionError('headers and row lengths are not equal')
        for i,r in enumerate(self): 
            if len(r) != width: raise AssertionError('row %d length differs from previous rows' %i)
        return True
