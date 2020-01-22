import os
import json
from azureml.core.model import Model
from spacy.cli.download import download as spacy_download
from nlp_architect.models.absa.inference.inference import SentimentInference

def init():
    """
    Set up the ABSA model for Inference  
    """
    global SentInference
    try:
        path = Model.get_model_path('absa')
    except:
        path = 'model'

    aspect_lex = os.path.join(path, 'generated_aspect_lex.csv')
    opinion_lex = os.path.join(path, 'generated_opinion_lex_reranked.csv')
    
    spacy_download('en')

    SentInference = SentimentInference(aspect_lex, opinion_lex)

def run(raw_data):
    """
    Evaluate the model and return JSON string
    """
    sentiment_doc = SentInference.run(doc=raw_data)
    parse = sentiment_doc.json().replace('doc_text', 'text').replace('"_', '"')
    print(json.dumps(json.loads(parse), indent=4))
    return doc2IO(parse)

def doc2IO(doc):
    """
    Converts ABSA doc to html output
    """
    doc_json = json.loads(doc)
    text = doc_json['text']
    aug_text = text
    for d in doc_json['sentences']:
        s = text[d['start']:d['end']+1]
        for ev in d['events']:
            for e in ev:
                typ = e['type']
                pol = e['polarity']
                txt = text[e['start']:e['start']+e['len']]
                s = s.replace(txt, f'<span class="{typ} {pol}">{txt}</span>')
                
        r = f'<span class="sentence">{s}</span>'
        aug_text = aug_text.replace(text[d['start']:d['end']+1], r, 1)

    doc_json['html'] = aug_text
    
    return doc_json

if __name__ == '__main__':
    import pprint
    init()

    docs = ["Loved the sweater but hated the pants",
        "Really great outfit, but the shirt is the wrong size",
        "I absolutely love this jacket! i wear it almost everyday. works as a cardigan or a jacket. my favorite retailer purchase so far"]

    for d in docs:
        print(f'\n---------------------\n{d}')
        r = run(d)
        print(json.dumps(r, indent=4))
