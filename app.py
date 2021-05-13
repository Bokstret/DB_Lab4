import csv
import re
import os
import time
import pymongo
from pymongo import MongoClient

part_size = 500
numbers = [1, 18, 19, 20, 21, 29, 30, 31, 39, 40, 41, 49, 50, 51, 59, 60, 61, 69, 70, 71, 79, 80, 81, 88, 89, 91, 98, 99, 101, 108, 109, 111, 118, 119, 121]
names = ['data', 'year', '_id', 'Birth', 'SEXTYPENAME', 'REGNAME', 'AREANAME', 'TERNAME', 'REGTYPENAME', 'TerTypeName', 'ClassProfileNAME', 'ClassLangName', 'EONAME', 'EOTYPENAME', 'EORegName', 'EOAreaName', 'EOTerName', 'EOParent', 'UkrTest', 'UkrTestStatus', 'UkrBall100', 'UkrBall12', 'UkrBall', 'UkrAdaptScale', 'UkrPTName', 'UkrPTRegName', 'UkrPTAreaName', 'UkrPTTerName', 'histTest', 'HistLang', 'histTestStatus', 'histBall100', 'histBall12', 'histBall', 'histPTName', 'histPTRegName', 'histPTAreaName', 'histPTTerName', 'mathTest', 'mathLang', 'mathTestStatus', 'mathBall100', 'mathBall12', 'mathBall', 'mathPTName', 'mathPTRegName', 'mathPTAreaName', 'mathPTTerName', 'physTest', 'physLang', 'physTestStatus', 'physBall100', 'physBall12', 'physBall', 'physPTName', 'physPTRegName', 'physPTAreaName', 'physPTTerName', 'chemTest', 'chemLang', 'chemTestStatus', 'chemBall100', 'chemBall12', 'chemBall', 'chemPTName', 'chemPTRegName', 'chemPTAreaName', 'chemPTTerName', 'bioTest', 'bioLang', 'bioTestStatus', 'bioBall100', 'bioBall12', 'bioBall', 'bioPTName', 'bioPTRegName', 'bioPTAreaName', 'bioPTTerName', 'geoTest', 'geoLang', 'geoTestStatus', 'geoBall100', 'geoBall12', 'geoBall', 'geoPTName', 'geoPTRegName', 'geoPTAreaName', 'geoPTTerName', 'engTest', 'engTestStatus', 'engBall100', 'engBall12', 'engDPALevel', 'engBall', 'engPTName', 'engPTRegName', 'engPTAreaName', 'engPTTerName', 'fraTest', 'fraTestStatus', 'fraBall100', 'fraBall12', 'fraDPALevel', 'fraBall', 'fraPTName', 'fraPTRegName', 'fraPTAreaName', 'fraPTTerName', 'deuTest', 'deuTestStatus', 'deuBall100', 'deuBall12', 'deuDPALevel', 'deuBall', 'deuPTName', 'deuPTRegName', 'deuPTAreaName', 'deuPTTerName', 'spaTest', 'spaTestStatus', 'spaBall100', 'spaBall12', 'spaDPALevel', 'spaBall', 'spaPTName', 'spaPTRegName', 'spaPTAreaName', 'spaPTTerName']
working = True

while working:
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client.zno_db
        coll = db.zno_coll

        start = time.time()
        for name in os.listdir('data'):
            year = re.findall(r'Odata(\d{4})File.csv', name)
            if year:
                with open(os.path.join('data', name), encoding='cp1251') as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    next(reader)
                    number = 0
                    part = list()
                    res = coll.find_one({'year' : year[0]}, sort=[('data', -1)])

                    if res:
                        if 'data' not in res:
                            print('Skip')
                            continue
                        for i in range(res['data'] + 1):
                            next(reader)
                            number += 1
                    
                    print('Start')
                    for row in reader:
                        part.append(dict(zip(names, [number] + year + row)))
                        number += 1

                        if not number % part_size:
                            coll.insert_many(part)
                            part = list()
                    if part:
                        coll.insert_many(part)
                        coll.update_many({}, {'$unset': {'data': 1}})
                        part = list()

        resul_time = time.time() - start
        with open('time.txt', 'w') as time_file:
            time_file.write(f'Result time: {resul_time}')

        select = [
            {"$match": {"mathTestStatus": 'Зараховано'}},
            {"$group": {"_id": {"region": "$REGNAME", "zno_year": "$year"}, "min": {"$min": "$mathBall"}}}]
        res = list(coll.aggregate(select))
        with open("result.txt", "w") as file:
            for item in res:
                file.write("%s\n" % item)
        working = False
    except Exception as error:
        print(error)
