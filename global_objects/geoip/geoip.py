#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Nico
@note: IP geolocation database parser + fast search
        i dunno where ever got this file
'''

import struct,socket



def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

class EverReader(object):
    def __init__(self,filename):
        self.__fn = filename;
        #self.reparse();

    def reparse(self,):
        print "Loading database..";
        pFile = open(self.__fn);
        data = pFile.readlines();
        pFile.close();
        #start ip, end ip, start ip int, end ip int, continent | country | province | city | district | IDONTKNOW, ASN?, Country, Country code, longitude, latitude
        rVal = dict();
        for i in data:
            line = i.split("|");
            rVal[int(line[2])] = {
                "range" : {
                    "start" : line[0],
                    "end" : line[1],
                    "__end_int" : int(line[3]),
                    "__start_int" : int(line[2])
                },
                "continent" : line[4],
                "country" : line[5],
                "province" : line[6],
                "city" : line[7],
                "district" : line[8],
                "longitude" : line[13],
                "latitude" : line[14].strip(),
            }
        self.__data = rVal;
        self.__data_keys = sorted(rVal.keys());
        print "Loaded %d records!" % len(self.__data_keys)

    def search(self,ip_address):
        '''
        B-Tree search
        :param ip_address:
        :return: info
        '''
        key = ip2int(ip_address);
        try:
            keys = self.__data_keys;
        except:
            self.reparse()
            keys = self.__data_keys;

        maxOffset = len(keys);
        minOffset = 0;
        middle = maxOffset / 2
        addend = middle;

        bottomCount = 0;
        d_compareCount = 0;
        #while not (key > self.__data_keys[middle] and key < self.__data_keys[middle + 1]) and bottomCount <= 5:

        condition = lambda x,y :  x >= self.__data[self.__data_keys[y]]['range']['__start_int'] and x <= self.__data[self.__data_keys[y]]['range']['__end_int']
        while not condition(key,middle) and bottomCount <= 8:
            #print "%d %d %d %d %d" % (maxOffset,minOffset,middle,addend,bottomCount)
            if key > keys[middle]:
                minOffset = middle;
                middle = maxOffset - (addend if addend else 1);
                #print "+"
            elif key < keys[middle]:
                maxOffset = middle;
                middle = minOffset + addend;
                #print "-"
            addend /= 2;
            if addend <= 1:
                bottomCount += 1;
            d_compareCount += 1;
            #print not (key > self.__data_keys[middle] and key < self.__data_keys[middle])
        #print "Number of comparisons: %d" % d_compareCount;
        return self.__data[self.__data_keys[middle]] if condition(key,middle) else {}