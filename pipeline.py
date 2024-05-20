from workers.filesplitter import FileSplitter
from workers.featuresminer import FeaturesMiner
from workers.materialssuppliersminer import MaterialsSuppliersMiner
from workers.instructor import Instructor
from workers.organizer import Organizer
import json
import time
import traceback

splitter = FileSplitter()
fminer = FeaturesMiner()
msminer = MaterialsSuppliersMiner()
instructor = Instructor()

def extraction_process(filetext):
    print("text length: ", len(filetext))
    
    start = time.time()
    sections = splitter.split_file_by_section(filetext)
    features = {}
    materials_suppliers = {}
    instruction = {}
    
    # Feature Extraction phase (Title, Authors, Tags)
    try:
        features = fminer.predict(sections['text'][:600])
        features = json.loads(features.choices[0].message.content)
    except Exception as e:
        print("Error extracting features:", e)
        traceback.print_exc()

    # Proceed with further processing if methods section exists
    if 'methods' in sections.keys():
        try:
            # Materials and Suppliers extraction phase
            for key, value in sections.items():
                print(f"Key: {key}, Value Length: {len(value)}")
            materials_suppliers = msminer.predict(sections['methods'])
            materials_suppliers = json.loads(materials_suppliers.choices[0].message.content)
            try:
                # Instruction phase
                instruction = instructor.predict(sections['methods'], materials_suppliers)
                instruction = json.loads(instruction.choices[0].message.content)
            except Exception as e:
                print('Error extracting instructions:', e)
                traceback.print_exc()
        except Exception as e:
            print('Error extracting materials and suppliers:', e)
            traceback.print_exc()
    else:
        try:
            # Materials and Suppliers extraction phase
            materials_suppliers = msminer.predict(sections['introduction'])
            materials_suppliers = json.loads(materials_suppliers.choices[0].message.content)
            try:
                # Instruction phase
                instruction = instructor.predict(sections['introduction'], materials_suppliers)
                instruction = json.loads(instruction.choices[0].message.content)
            except Exception as e:
                print('Error extracting instructions:', e)
                traceback.print_exc()
        except Exception as e:
            print('Error extracting materials and suppliers:', e)
            traceback.print_exc()

    try:
        organizer = Organizer()
        
        # JSON files merging
        merged_data = [
            features,
            materials_suppliers,
            instruction
        ]
        print("\n\n Data Merged Successfully!")
        
        # Organizing phase
        try:
            organizer.process_json(merged_data)
        except Exception as e:
            print("Error storing paper:", e)
            traceback.print_exc()
        
        organizer.close()
        end = time.time()
        print(f"Process done! - {round(end - start)}s")

    except Exception as e:
        print('Error merging and storing JSONs:', e)
        traceback.print_exc()
