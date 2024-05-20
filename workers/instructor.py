from openai import OpenAI
import os
import json

class Instructor:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        print('Instructor Initialized')
    
    def predict(self, section_text, experiments):
        print('Instructor Generating Instructions...')
        prediction = self.client.chat.completions.create(
        model='gpt-4-turbo',
        temperature=1.0,
        messages=[
            {'role':'system','content':'''you're an ner system used to extract and form instructions and methodolgies to help researcher do an experiment from a given text and form it in a JSON file.
                                            the output should be in this structure:
                                            "experiments": [
                                                    {
                                                        "experiment_title": "Experiment1",
                                                        "experiment_items": [
                                                            {"material": "Material1", "supplier": "Supplier1", "material_usage": "Usage1"},
                                                            {"material": "Material2", "supplier": "Supplier2", "material_usage": "Usage2"}
                                                        ],
                                                        "methodologies": ["Methodology1"],
                                                        "instructions": ["Instruction1"]
                                                    }
                                                ]
                                            }
                                        ]
                                        given a json file with all mentioned experiments to add the instruction and methodolgies for each one
                                        return only json format.'''},
            {'role':'user', 'content':section_text[:4050]},
            {'role':'user', 'content':section_text[4050:] if len(section_text[4050:]) < 4050 else section_text[4050:4050+4050]},
            {'role':'user', 'content':json.dumps(experiments)},


        ]
    )    
        print(prediction)
        return prediction
