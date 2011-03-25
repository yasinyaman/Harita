#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pymongo
db = pymongo.Connection().harita
f = open("iller.js","r").readlines()
for i in f:
    v1 = i.split(",")[0].split(":")[1]
    v2 = i.split(",")[1].split(":")[1].replace("\n","").replace("}","").replace("\"","")
    db.iller.save({"plaka":v1,"il":v2})
