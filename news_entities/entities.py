import json

import spacy

from news_entities.articles import Article

nlp = spacy.load('en_core_web_sm')
desired_labels = [
    'PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'LAW', 'PER'
]
desired_labels = [
    'PERSON', 'ORG'
]
ENTITY_ID_COUNTER = 0
OCCURENCE_ID_COUNTER = 0

def detect_entities(article):
    results = [
        nlp(paragraph) for paragraph in article.body
    ]
    entities = []
    occurences = []
    for index, result in enumerate(results):
        for entity in result.ents:
            if entity.label_ in desired_labels:
                entity_object = Entity(entity)
                entities.append(entity_object)
                
                occurence_object = Occurence(
                    article = article,
                    entity = entity_object,
                    paragraph_index = index,
                    start_char = entity.start_char,
                    end_char = entity.end_char
                )
                occurences.append(occurence_object)
    return entities, occurences

def clean_label(label):
    label = label.lower()
    if label[-2:] == "'s":
        label = label[:-2]
    label = label.replace(' ', '_')
    return label

class Entity(object):
    def __init__(self, entity):
        self.label = clean_label(str(entity))
        self.type = str(entity.label_)
        self.dupes = []

        global ENTITY_ID_COUNTER
        self.id = ENTITY_ID_COUNTER
        ENTITY_ID_COUNTER += 1

    


class Occurence(object):
    def __init__(self, article, entity, paragraph_index, start_char, end_char):
        self.article_id = article.id
        self.entity_id = entity.id
        self.paragraph_index = paragraph_index
        self.start_char = start_char
        self.end_char = end_char

        global OCCURENCE_ID_COUNTER
        self.id = OCCURENCE_ID_COUNTER
        OCCURENCE_ID_COUNTER += 1

if __name__ == '__main__':
    with open('./test.json') as f:
        documents = json.load(f)
    
    all_entities = {}
    all_occurences = {}
    for item in documents:
        article = Article(**documents[item])
        entities, occurences = detect_entities(article)
        for ent in entities:
            all_entities[ent.id] = ent.__dict__
        for occ in occurences:
            all_occurences[occ.id] = occ.__dict__
    with open('entities.json', 'w') as f:
        json.dump(all_entities, f, indent=4)
    with open('occurences.json', 'w') as f:
        json.dump(all_occurences, f, indent=4)
