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

    if 'background' in sections.keys():
        # Feature Extraction phase (Title, Authors, Tags)
        features = fminer.predict(sections['background'])
        features = json.loads(features.choices[0].message.content)
    else:
        # Feature Extraction phase (Title, Authors, Tags)
        features = fminer.predict(sections['introduction'])
        features = json.loads(features.choices[0].message.content)
    
    if 'methods' in sections.keys():
        try:
            # Materials and Suppliers extraction phase
            materials_suppliers = msminer.predict(sections['methods'])
            materials_suppliers = json.loads(materials_suppliers.choices[0].message.content)
            try:
                # Instruction phase
                Instruction = instructor.predict(sections['methods'])

                Instruction = json.loads(Instruction.choices[0].message.content)
            except:
                print('Instrcutor cannot give steps for this one!')
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
                print('Instrcutor cannot give steps for this one!')
        except:
            print('No Materials or Suppliers Found!')


    
    try:
        #json files merging
        merged_data = [
            features,
            materials_suppliers,
            Instruction
        ]
    except:
        print('Can\'t merge jsons!')
    
    # Organizing phase
    organizer.process_json(merged_data)
    organizer.close()
    print("Organizer Saved information in database successfully!")

    end = time.time()

    print(f"process done! - {round(end - start)}s")