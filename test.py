from workers.filesplitter import FileSplitter
from workers.featuresminer import FeaturesMiner
from workers.materialssuppliersminer import MaterialsSuppliersMiner
from workers.instructor import Instructor
from workers.organizer import Organizer
import json 
import time



start = time.time()
splitter = FileSplitter()
sections = splitter.split_file_by_section('file.txt')
print(sections.keys())
end = time.time()
print("Calculated time for splitting: ",end - start)

start = time.time()

FMiner = FeaturesMiner()
predictions = FMiner.predict(sections['background'])

results = json.loads(predictions.choices[0].message.content)
print(results)

end = time.time()
print("Calculated time for FeaturesMiner: ",end - start)


print('\n Phase2 \n')

start = time.time()
Ins = Instructor()
pred = Ins.predict(sections['methods'])

results = json.loads(pred.choices[0].message.content)
print(results)

end = time.time()
print("Calculated time for Instructor: ",end - start)


print('\n Phase3 \n')

start = time.time()
MSM = MaterialsSuppliersMiner()
pred = MSM.predict(sections['methods'])

results = json.loads(pred.choices[0].message.content)
print(results)

end = time.time()
print("Calculated time for MaterialsSuppliersMiner: ",end - start)

start = time.time()
print('\n Phase4 \n')
'''org = Organizer('railway',
                      'postgres',
                      'B*Cc6Ga2cac1EDE6dFggC*6F-ge25aGD',
                      'roundhouse.proxy.rlwy.net',
                      '57938')

'''
print("Calculated time for Organizer: ",end - start)
end = time.time()
