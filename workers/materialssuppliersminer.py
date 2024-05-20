from openai import OpenAI
import os 
class MaterialsSuppliersMiner:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        print('MaterialsSuppliersMiner Initialized')

    
    def predict(self, section_text):
        print('MaterialsSuppliersMiner Mining for Materials and Suppliers...')
        prediction = self.client.chat.completions.create(
        model='gpt-4-turbo',
        temperature=1.0,
        messages=[
            {'role':'system','content':'''you're an ner system used to extract features from a given text and form it in a JSON file
                                        the output should be in this structure.
                                        you should extract materials and suppliers and experiments and catalog them in this structure.

                                        {
                                        experiments: [
                                        {
                                        "experiment_title" : "output_title",
                                        "experiment_items" : [ {"material" : "output_material" , "supplier" : "output_supplier", "material_usage":"output_material_usage"}, ... ],
                                        },
                                        {
                                        "experiment_title" : "output_title",
                                        "experiment_items" : [ {"material" : "output_material" , "supplier" : "output_supplier","material_usage":"output_material_usage"}, ... ],
                                        },
                                        ...
                                        ]
                                        }
                                        return only json format.'''},
            {'role':'user', 'content':section_text[:4050]},
            {'role':'user', 'content':section_text[4050:] if len(section_text[4050:]) < 4050 else section_text[4050:4050+4050]},

            ]
            )    
        print(prediction)

        return prediction