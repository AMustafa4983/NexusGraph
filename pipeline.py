from workers.filesplitter import FileSplitter
from workers.featuresminer import FeaturesMiner
from workers.materialssuppliersminer import MaterialsSuppliersMiner
from workers.instructor import Instructor
from workers.organizer import Organizer
import json 
import time


splitter = FileSplitter()
fminer = FeaturesMiner()
msminer = MaterialsSuppliersMiner()
instructor = Instructor()
organizer = Organizer('railway',
                'postgres',
                'ba**64B3f3*dd521Egef3g4*B-E-cA-3',
                'viaduct.proxy.rlwy.net',
                '36793')

def extraction_process(filetext):
    start = time.time()
    # Splitting Phase
    sections = splitter.split_file_by_section(filetext)
    print("The extracted sections are: ",sections.keys())

    if 'background' in sections.keys():
        # Feature Extraction phase (Title, Authors, Tags)
        features = fminer.predict(sections['background'])
        features = json.loads(features.choices[0].message.content)
        print("Extracted features formed in json file: ",features)
    else:
        # Feature Extraction phase (Title, Authors, Tags)
        features = fminer.predict(sections['introduction'])
        features = json.loads(features.choices[0].message.content)
        print("Extracted features formed in json file: ",features)
    
    if 'methods' in sections.keys():

        # Materials and Suppliers extraction phase
        materials_suppliers = msminer.predict(sections['methods'])
        materials_suppliers = json.loads(materials_suppliers.choices[0].message.content)
        print("Materials and Suppliers formed in json file: ", materials_suppliers)

        # Instruction phase
        Instruction = instructor.predict(sections['methods'])

        Instruction = json.loads(Instruction.choices[0].message.content)
        print("instuction formed in json file: ", Instruction)

    else:
        # Materials and Suppliers extraction phase
        materials_suppliers = msminer.predict(sections['introduction'])
        materials_suppliers = json.loads(materials_suppliers.choices[0].message.content)
        print("Materials and Suppliers formed in json file: ", materials_suppliers)

        # Instruction phase
        Instruction = instructor.predict(sections['introduction'])

        Instruction = json.loads(Instruction.choices[0].message.content)
        print("instuction formed in json file: ", Instruction)
    
    #json files merging
    merged_data = [
        features,
        materials_suppliers,
        Instruction
    ]
    print("Merged File: ",merged_data)

    # Organizing phase
    organizer.process_json(merged_data)
    organizer.close()
    print("Organizer Saved information in database successfully!")
    end = time.time()

    print(f"process done! - {end - start}s")