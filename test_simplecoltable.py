#!/usr/bin/env python
"""unittests for simpletable
"""

import unittest2 as unittest
import simplecoltable
#from ordereddict import OrderedDict
from collections import OrderedDict
import csv
import os
import copy

def get_country_data():
    modulepath = os.path.dirname(__file__)       
    with open(os.path.join(modulepath,'countries.csv')) as csvfile:
        reader = csv.reader(csvfile)
        header = reader.next()
        data = list(reader)
    return header, data

header, data = get_country_data()
data2 = simplecoltable.rows2dict(header,data)


class TestTable(unittest.TestCase):
    """test basic usage of Table class"""
    @classmethod
    def setUpClass(cls):
        cls.tab = simplecoltable.ColTable(data2)
    
    @classmethod
    def tearDownClass(cls):
        del cls.tab
        
    def setUp(self):
        pass
        
    def tearDown(self):
        pass        
        
    def test_Construction(self):
        #possible data input
        self.assertIsNotNone(simplecoltable.ColTable(data2)) #supplying an ordereddict
        self.assertIsNotNone(simplecoltable.ColTable(dict(data2))) # via a dict (ordering lost though)
        self.assertIsNotNone(simplecoltable.ColTable(tuple((k,v) for k,v in data2.items()))) #via a tuple
        
        #data inconsistancies
        ##cols inconsistant lengths
        tmp = copy.copy(data2)
        tmp[header[1]] = data2[header[1]][:-1]
        self.assertRaises(AssertionError,simplecoltable.ColTable,tmp)
        
    def test_emptryclass(self):
        tab = simplecoltable.ColTable()
        tab.width
        tab.validate()
        tab.headers = header
        tab.append(data[0])
        #tab.extend(data[1:10]) #extend not implemented
        tab2 = simplecoltable.ColTable((k,[]) for k in header)
        tab2.width
        tab2.validate()
        tab2.append(data[0])
        #tab2.extend(data[1:10]) #extend not implemented      
    
    def test_getrowitem(self):
        expected = OrderedDict((k,v) for k,v in zip(header,data[0]))
        self.assertEqual(self.tab[0],expected)
        self.assertIsInstance(self.tab[0],type(expected))
        expected2 = OrderedDict((k,v) for k,v in zip(header,data[-1]))
        self.assertEqual(self.tab[-1],expected2)
        
    def test_getcolitem(self):
        self.assertEqual(len(self.tab[header[2]]),len(self.tab))
               
    def test_rowslice(self):
        tmp = self.tab[1:4]
        width = self.tab.width
        self.assertEqual(len(tmp),3)
        self.assertTrue(all(len(row) == width for row in tmp))
        self.assertIsInstance(tmp,simplecoltable.ColTable)
        tmp2 = self.tab[slice(1,4)] #explicit slice
        self.assertEqual(len(tmp2),3)
        self.assertTrue(all(len(row) == width for row in tmp2))
        self.assertEqual(tmp,tmp2)
        tmp3=self.tab[1:10:2] #slice with strides
        self.assertEqual(len(tmp3),5)
        self.assertTrue(all(len(row) == width for row in tmp2))
        
    def test_setrowitem(self):
        tab = simplecoltable.ColTable(data2) #fresh table
        width = tab.width
        length = len(tab)      
        headers = list(tab.headers)
        #good insertions
        entry = [2]*width #no type checking, only width
        for e in entry,tuple(entry): #numpy array?
            idx = 10
            tab[idx] = e
            self.assertEqual(len(tab),length)
            self.assertEqual(tab.width,width)
            self.assertEqual(tab.headers,headers)
            self.assertTrue(tab.validate())
        #bad insertions
        entry = [2]*(width + 11)
        for e in entry,tuple(entry): #numpy array?
            idx = 10
            self.assertRaises(ValueError,tab.__setitem__,idx,e)
            self.assertEqual(len(tab),length)
            self.assertEqual(tab.width,width)
            self.assertEqual(tab.headers,headers)
            self.assertTrue(tab.validate())  

    def test_setcolitem(self):
        #create an instance with mutable rows (lists not tuples)
        tab = simplecoltable.ColTable(data2)
        width = tab.width
        length = len(tab)
        headers = list(tab.headers)
        #good insertions
        entry = [2]*length #no type checking, only length
        for e in entry,tuple(entry): #numpy array?
            idx = 'iso3'
            tab[idx] = e
            self.assertEqual(len(tab),length)
            self.assertEqual(tab.width,width)
            self.assertEqual(tab.headers,headers)
            self.assertTrue(tab.validate())
        #bad insertions
        entry = [2]*(length-1)
        for e in entry,tuple(entry): #numpy array?
            idx = 'iso3'
            self.assertRaises(ValueError,tab.__setitem__,idx,e)
            self.assertEqual(len(tab),length)
            self.assertEqual(tab.width,width)
            self.assertEqual(tab.headers,headers)
            self.assertTrue(tab.validate())           
        
    def test_setbyslice(self):
        #test __setslice__
        ##test for success
        #?
        ##test for failure
        #?
        #test __setitem__ with slice object
        ##test for success
        #?
        ##test for failure
        #?
        #test __setitem__ with slice object and stride
        ##test for success
        #?
        ##test for failure
        #?
        pass
    
    def test_appendrowitem(self):
        tab = simplecoltable.ColTable(data2) #fresh table
        #tab = tab[:] #copy column lists so that data2 is not affected
        width = tab.width
        length = len(tab)       
        entry = [2]*width #no type checking, only length
        for e in entry,tuple(entry): #numpy array?
            tab.append(e)
            length += 1
            self.assertEqual(len(tab),length)
            self.assertEqual(tab.width,width)
        #generator fail check
        self.assertRaises(TypeError,tab.append,(i for i in entry))
        #bad insertion tests
        entry2 = [2]*(width-1) #no type checking, only length
        for e in entry2,tuple(entry2): #numpy array?
            self.assertRaises(ValueError,tab.append,e)
            self.assertTrue(tab.validate())

    def test_insertrowitem(self):
        tab = simplecoltable.ColTable(data2) #fresh table
        width = tab.width
        length = len(tab)       
        entry = [2]*width #no type checking, only length
        for e in entry,tuple(entry): #numpy array?
            idx = 1
            tab.insert(idx,e)
            length += 1
            self.assertEqual(len(tab),length)
            self.assertEqual(tab.width,width)
        #generator fail check
        self.assertRaises(TypeError,tab.append,(i for i in entry))
        #bad insertion tests
        entry2 = [2]*(width-1) #no type checking, only length
        for e in entry2,tuple(entry2): #numpy array?
            self.assertRaises(ValueError,tab.insert,idx,e)
            self.assertTrue(tab.validate())

    def test_appendcolitem(self):
        tab = simplecoltable.ColTable(data2) #fresh table
        width = tab.width
        length = len(tab)
        entry = [2]*length #no type checking, only length
        for i,e in enumerate((entry,tuple(entry))): #numpy?
            colname = 'OhYeah' + str(i)
            tab[colname] = e
            self.assertEqual(len(tab),length)
            width += 1
            self.assertEqual(tab.width,width)
            self.assertIn(colname,tab.headers)
        #generator fail check
        self.assertRaises(TypeError,tab.__setitem__,'test',(i for i in entry))
        #bad insertion tests
        entry2 = [2]*(length+1) #no type checking, only length
        for i,e in enumerate((entry2,tuple(entry2))): #numpy array?
            colname = 'OhYeah' + str(i)
            def test(): tab[colname] = e
            self.assertRaises(ValueError,test)
            self.assertTrue(tab.validate())

    def test_insertcolitem(self):
        tab = simplecoltable.ColTable(data2) #fresh table
        width = tab.width
        length = len(tab)
        headers = list(tab.headers)
        entry = [2]*length #no type checking, only length
        for i,e in enumerate((entry,tuple(entry))): #numpy array?
            idx = 1
            colname = 'OhYeah' + str(i)
            tab.insertcol(idx,colname,e)
            self.assertEqual(len(tab),length)
            width += 1
            headers.insert(idx,colname)
            self.assertEqual(tab.width,width)
            self.assertIn(colname,tab.headers)
            self.assertEqual(tab.headers,headers)
        #generator fail check
        idx = 1
        self.assertRaises(TypeError,tab.insertcol,idx,'test',(i for i in entry))
        #bad insertion tests
        entry2 = [2]*(length+1) #no type checking, only length
        for i,e in enumerate((entry2,tuple(entry2))): #numpy array?
            idx = 1
            colname = 'OhYeah' + str(i)
            def test(): tab[colname] = e
            self.assertRaises(ValueError,tab.insertcol,idx,colname,e)
            self.assertTrue(tab.validate())
    
    def test_delrowitem(self):
        tab = self.tab
        width = tab.width
        length = len(tab)
        del tab[1]
        self.assertEqual(len(tab),length-1)
        self.assertEqual(tab.width,width)

    def test_delcolitem(self):
        #create an instance with mutable rows (lists not tuples)
        tab = simplecoltable.ColTable(data2)
        width = tab.width
        length = len(tab)
        col = tab.headers[0]
        del tab[col]
        self.assertEqual(len(tab),length)
        self.assertEqual(tab.width,width-1)
        self.assertNotIn(col,tab.headers)
    
    def test_validate(self):
        #create a disposable instance
        tab = simplecoltable.ColTable(data2)
        #tab = tab[:] #copy column lists so that data2 is not affected
        #test col violation
        tab[header[1]].pop() #shorten 2nd column - mutating a retrieved row evades checks
        self.assertRaises(AssertionError,tab.validate)
        
    def test_headers(self):
        h = list(header) #copy
        h.pop()
        self.assertRaises(ValueError,setattr,self.tab,'headers',h)
        h.extend(['a','t'])
        self.assertRaises(ValueError,setattr,self.tab,'headers',h)
        self.tab.headers = [h.upper() for h in header]
        self.assertEqual(self.tab.headers,[h.upper() for h in header])
        self.tab.headers = tuple(header) #reset to original header
        self.assertEqual(self.tab.headers,header)

if __name__ == '__main__':
    unittest.main()
