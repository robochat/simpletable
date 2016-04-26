#!/usr/bin/env python
"""A very simple table classes written in pure python. It allows us to
index the data either by row index (integer) or by column (text label).

The code is inspired by the module tablib but is vastly simplified. For
instance tablib provides automatic validation of insertions etc during 
normal operations and can export and import data to many formats.
"""

class Table(list):
    """A very simple table class that supports index and column indexing.
    
    There is a basic validation method that checks that each row is the
    same length but nothing apart from that.
    """    
    def __init__(self, *args, **kwargs):
        """Takes an iterable. Can also use the keyword argument 'headers' to 
        set the column headers.
        """        
        list.__init__(self, *args)
        self.title = kwargs.pop('title',None)
        self.headers = kwargs.pop('headers',None)
        
        if kwargs: raise TypeError('got an unexpected keyword argument %s',kwargs.pop())
        
    def __getitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            if key in self.headers:
                pos = self.headers.index(key) # get 'key' index from each data
                return [row[pos] for row in self]
            else:
                raise KeyError
        else:
            return super(Table,self).__getitem__(key)
    
    def __setitem__(self, key, value):
        if isinstance(key, str) or isinstance(key, unicode):
            assert len(value) == len(self), 'new column is not the correct length'
            if key in self.headers:
                pos = self.headers.index(key)
                for i,(row,val) in enumerate(zip(self,value)):
                    #Add code here to handle row types other than list and tuple
                    if type(row) == list: 
                        row[pos] = val
                    elif type(row) == tuple:
                        newrow = row[:pos] + (val,) + row[pos+1:] #should I respect immutability of tuple?
                        super(Table,self).__setitem__(i,newrow)
                    else:
                        raise TypeError('row entry is an unhandled sequence type')
            else:
                self.headers.append(key)
                for i,(row,val) in enumerate(zip(self,value)): 
                    #Add code here to handle row types other than list and tuple
                    if type(row) == list: 
                        row.append(val)
                    elif type(row) == tuple:
                        newrow = row + (val,) #should I respect immutability of tuple?
                        super(Table,self).__setitem__(i,newrow)
                    else:
                        raise TypeError('row entry is an unhandled sequence type')
        else:
            super(Table,self).__setitem__(key,value)
    
    def __delitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            if key in self.headers:
                pos = self.headers.index(key)
                del self.headers[pos]
                for i, row in enumerate(self):
                    del row[pos]
                    self[i] = row
            else:
                raise KeyError
        else:
            super(Table,self).__delitem__(key)

    def __repr__(self):
        try:
            return '<%s table: %s: %d entries>' % (self.title or 'unnamed',','.join(self.headers),len(self))
        except AttributeError:
            return '<table object>'
            
    def validate(self):
        """checks that all rows have the same length"""
        width = len(self[0])
        assert len(self.headers) == width, 'headers and row lengths are not equal'
        for i,r in enumerate(self): assert len(r) == width, 'row %d length differs from previous rows' %i
