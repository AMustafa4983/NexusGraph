from openai import OpenAI
import os

class FeaturesMiner:
    def __init__(self):
        
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        print('FeaturesMiner Initialized')
    
    def predict(self, section_text):
        print('FeaturesMiner Mining for Titles and Authors...')
        prediction = self.client.chat.completions.create(
            model='gpt-4-turbo',
            temperature=1.0,
            messages=[
                {'role':'system','content':'''you're an ner system used to extract features from a given text and form it in a JSON file
                                            the output should be in this structure.
                                            {
                                            "title" : "output_title",
                                            "authors" : [ {"name" : "output_name" , "affiliation" : "output_affiliation"}, ... ],
                                            "tags": ["tag1", "tag2",  ..],
                                            }
                                            return only json format.
                                            tags are the paper categories mentioned in the text.'''},
                {'role':'user', 'content':section_text[:600]},

            ]
        )
        print(prediction)
        return prediction