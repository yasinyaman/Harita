#!/usr/bin/env python
#-*- coding:utf-8 -*-

def mapreduce():
    import pymongo
    db = pymongo.Connection().harita
    map = "function() { emit(this.il, {count: 1});}"
    reduce = "function(key, values) {  var sum = 0;  values.forEach(function(doc) {    sum += doc.count;  });  return {count: sum};};"
    result = db.kullanici.map_reduce(map, reduce)
    return result.find()
