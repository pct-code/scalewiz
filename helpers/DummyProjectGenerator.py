import os
import json

from Test import Test

def run():

    path = os.path.abspath(r"C:\Users\P\source\repos\scalewiz\helpers\dummy.json")

    tests = []

    this = {
            "info":{
                "customer": "pct",
                "submittedBy": "alex",
                "productionCo": "pct",
                "field": "field",
                "sample": "sample",
                "sampleDate": "11/16/2020",
                "recDate": "11/16/2020",
                "compDate": "11/16/2020",
                "name": "dummy",
                "numbers": "0 - 0",
                "path": path
            },
            "params": {
                "bicarbonates": 1000,
                "bicarbsIncreased": False,
                "chlorides": 10000,
                "baseline": 75,
                "temperature": 200,
                "limitPSI": 1500,
                "limitMin": 90,
                "interval": 3,
                "uptake": 15
            },
    }

    maxreadings = round(this.get('params').get('limitMin') * 60 / this.get('params').get('interval')) + 1
    step = round(this.get('params').get('limitPSI') / maxreadings)
                
    for i in range(5):
        test = Test()
        test.name.set(f"Test {i}")
        test.isBlank.set(False)
        test.clarity.set("Clear")
        for j in range(maxreadings):
            test.readings.append({
                "elapsedMin": round( 0.05 * j, 2),
                "pump 1": round(j * 0.5 * step),
                "pump 2": round(j * 1.5 * step)
            })
            if (test.readings[j]["pump 2"] >= this.get('params').get('limitPSI')):
                break
        print(f"{test.name.get()} has {len(test.readings)} readings")
        tests.append(test.dumpJson())


    for i in range(3):
        test = Test()
        test.name.set(f"Blank {i}")
        test.isBlank.set(True)
        for j in range(maxreadings):
            test.readings.append({
                "elapsedMin": round( 0.05 * j, 2),
                "pump 1": round(j * step),
                "pump 2": round(j * 2 * step)
            })
            if (test.readings[j]["pump 2"] >= this['params']['limitPSI']):
                break
        print(f"{test.name.get()} has {len(test.readings)} readings")
        tests.append(test.dumpJson())
    

    this['tests'] = tests
    with (open(path, 'w') as file):
        json.dump(this, file, indent=4)





    
            