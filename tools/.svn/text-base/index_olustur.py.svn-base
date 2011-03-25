#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pymongo

db = pymongo.Connection().harita

if db.kullanici.create_index([("koordinatlar",pymongo.GEO2D)]):
    print "Oluşturuldu"

