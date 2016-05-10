#!/usr/bin/env python
"""unittests for simpletable
"""

import unittest2 as unittest
import simpletable
import sqlite3
import os
import copy

def get_country_data():
    modulepath = os.path.dirname(__file__)
    with sqlite3.connect(os.path.join(modulepath,'country_codes.sqlite')) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Countries;")
        result = cur.fetchall()
        cur.close()
    return result

data = get_country_data()
header = ['iso2','iso3','num','name','pop']



class TestTable(unittest.TestCase):
    """test basic usage of Table class"""
    @classmethod
    def setUpClass(cls):
        cls.tab = simpletable.Table(data,headers=header,title='countrycodes')
    
    @classmethod
    def tearDownClass(cls):
        del cls.tab
        
    def setUp(self):
        pass
        
    def tearDown(self):
        pass        
        
    def test_Construction(self):
        #header variations
        self.assertRaises(AssertionError,simpletable.Table,data)
        self.assertRaises(AssertionError,simpletable.Table,data,headers=[])
        self.assertIsNotNone(simpletable.Table(data,headers=tuple(header)))
        h = list(header) #copy
        h.pop()
        self.assertRaises(AssertionError,simpletable.Table,data,headers=h)
        h.extend(['a','t'])
        self.assertRaises(AssertionError,simpletable.Table,data,headers=h)
        
        #data inconsistancies
        ##rows inconsistant lengths
        tmp = copy.copy(data)
        tmp[1] = data[0][:-1]
        self.assertRaises(AssertionError,simpletable.Table,tmp,headers=header)
        
    def test_emptryclass(self):
        tab = simpletable.Table()
        tab.width
        tab.validate()
        #tab.headers = header ??
        tab.append(data[0])
        tab.extend(data[1:10])
        tab2 = simpletable.Table(headers=header)
        tab2.width
        tab2.validate()
        tab2.append(data[0])
        tab2.extend(data[1:10])        
    
    def test_getrowitem(self):
        self.assertEqual(self.tab[0],data[0])
        self.assertIsInstance(self.tab[0],type(data[0]))
        self.assertEqual(self.tab[-1],data[-1])
        
    def test_getcolitem(self):
        self.assertEqual(len(self.tab[header[2]]),len(self.tab))
               
    def test_rowslice(self):
        tmp = self.tab[1:4] # handled by deprecated __getslice__() method
        width = self.tab.width
        self.assertEqual(len(tmp),3)
        self.assertTrue(all(len(row) == width for row in tmp))
        self.assertIsInstance(tmp,simpletable.Table)
        tmp2 = self.tab[slice(1,4)] #explicit slices are handled by __getitem__ and not deprecated __getslice__ method
        self.assertEqual(len(tmp2),3)
        self.assertTrue(all(len(row) == width for row in tmp2))
        self.assertEqual(tmp,tmp2)
        tmp3=self.tab[1:10:2] #slices with strides are handled by __getitem__ and not deprecated __getslice__ method
        self.assertEqual(len(tmp3),5)
        self.assertTrue(all(len(row) == width for row in tmp2))
        
    def test_setrowitem(self):
        pass

    def test_setcolitem(self):
        pass
        
    def test_setbyslice(self):
        pass
    
    def test_appendrowitem(self):
        pass
        #list,tuple,numpy - no type checking, only length
        #generator fail check

    def test_appendcolitem(self):
        pass
        #list,tuple,numpy - no type checking, only length
        #generator fail check

    def test_insertcolitem(self):
        pass
        #list,tuple,numpy - no type checking, only length
        #generator fail check
    
    def test_delrowitem(self):
        tab = self.tab
        width = tab.width
        length = len(tab)
        del tab[1]
        self.assertEqual(len(tab),length-1)
        self.assertEqual(tab.width,width)

    def test_delcolitem(self):
        #create an instance with mutable rows (lists not tuples)
        tab = simpletable.Table((list(row) for row in self.tab),headers=self.tab.headers)
        width = tab.width
        length = len(tab)
        col = tab.headers[0]
        del tab[col]
        self.assertEqual(len(tab),length)
        self.assertEqual(tab.width,width-1)
        self.assertNotIn(col,tab.headers)
    
    def test_validate(self):
        pass
        
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
