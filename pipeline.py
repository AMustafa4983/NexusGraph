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


def extraction_process(filetext):
    print("text length: ", len(filetext))
    
    start = time.time()
    # Splitting Phase
    sections = splitter.split_file_by_section(filetext)
    features = {}

    # Feature Extraction phase (Title, Authors, Tags)
    try:
        features = fminer.predict(sections['text'][:600])
        features = json.loads(features.choices[0].message.content)
    except:
        print("Needed background not found in this paper!")
    
    # Proceed with further processing
    if 'methods' in sections.keys():
        try:
            # Materials and Suppliers extraction phase
            for key, value in sections.items():
                print(f"Key: {key}, Value Length: {len(value)}")
            materials_suppliers = msminer.predict(sections['methods'])
            materials_suppliers = json.loads(materials_suppliers.choices[0].message.content)
            try:
                # Instruction phase
                Instruction = instructor.predict(sections['methods'])
                Instruction = json.loads(Instruction.choices[0].message.content)
            except:
                print('Instructor cannot give steps for this one!')
        except:
            print('No Materials or Suppliers Found')

    else:
        try:
            # Materials and Suppliers extraction phase
            materials_suppliers = msminer.predict(sections['introduction'])
            materials_suppliers = json.loads(materials_suppliers.choices[0].message.content)
            try:
                # Instruction phase
                Instruction = instructor.predict(sections['introduction'])

                Instruction = json.loads(Instruction.choices[0].message.content)
            except:
                print('Instructor cannot give steps for this one!')
        except:
            print('No Materials or Suppliers Found!')

    # JSON files merging
    merged_data = [
        features,
        materials_suppliers,
        Instruction
    ]
    print("\n\n Data Merged Successfully!")
    # Organizing phase
    organizer = Organizer('railway',
                'postgres',
                'ba**64B3f3*dd521Egef3g4*B-E-cA-3',
                'viaduct.proxy.rlwy.net',
                '36793')
    organizer.process_json(merged_data)
    organizer.close()
    end = time.time()
    print(f"Process done! - {round(end - start)}s")

    print("Organizer saved information in the database successfully!")
'''    try:
    except:
        print('Can\'t merge JSONs!')
'''     