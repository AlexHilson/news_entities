import re
from toolz.curried import *

def load_file(fname):
    '''
    Extract articles from Nexis file, 
    ignoring results with less than 2 lines.

    Returns headlines and articles
    '''
    new_doc_regex = re.compile(
        '.*[0-9]* of [0-9]* DOCUMENTS.*'
    )
    results = pipe(
        fname,
        open,
        lambda file: file.readlines(),
        partitionby(new_doc_regex.match),
        filter(lambda article: len(article) > 1)
    )
    headlines = next(results)
    return headlines, results

def extract_article_header(article):
    '''
    Given article as a list of lines, classify
    headline, body, and uncategorised liens
    '''
    uncategorised = []
    body = []
    headline = None
    for index, line in enumerate(article):
        line = line.strip()
        if line.startswith('BODY:'):
            body = article[index+1:]
            break
        if line.startswith('HEADLINE:'):
            headline = line.strip()
        else:
            uncategorised.append(line.strip())
    if len(body) == 0:
        raise ValueError('no body found')
    return headline, uncategorised, body

def extract_article_footer(article):
    '''
    Given article as a list of lines.
    This is a bit less certain than header gathering
    '''
    uncategorised = []
    body = []
    for index, line in enumerate(article):
        line = line.strip()
        if '----------' in line:
            line = ''
        if line.startswith('LANGUAGE:'):
            [
                uncategorised.append(footer_line.strip())
                for footer_line in article[index:]
            ]
            break
        if line.startswith('Source: '):
            uncategorised.append(line.strip())
        elif 'copyright' and 'all rights reserved' in line.lower():
            uncategorised.append(line.strip())
        else:
            body.append(line)
    body = partitionby(lambda line: len(line) == 0, body)
    paragraphs = list(map(lambda group: ' '.join(group), body))
    useful_paragraphs = list(
        filter(
            lambda para: len(para) > 0 or
            (len(para) == 1 and len(para[0].strip() == 0)),
            paragraphs))
    return uncategorised, useful_paragraphs

def decompose_article(article):
    headline, uncategorised, other = extract_article_header(article)
    footer, body = extract_article_footer(other)
    uncategorised.extend(footer)
    return headline, body, uncategorised

class Article(object):
    def __init__(self, id, headline, body, metadata):
        self.headline = headline
        self.body = body
        self.id = id
        self.metadata = metadata

def test():
    _, loaded_file = load_file('./sample.txt')
    sample = next(loaded_file)
    header, body, metadata = decompose_article(sample)
    assert header == 'HEADLINE: FAA type certifies P&W engine'
    assert 'AirFinance Journal' in metadata
    assert 'LANGUAGE: ENGLISH' in metadata
    assert len(body) == 6

if __name__ == '__main__':
    test()
    _, loaded_file = load_file('./sample.txt')
    results = {}
    for index, article in enumerate(loaded_file):
        header, body, metadata = decompose_article(article)
        article_object = Article(
            id = index,
            headline = header,
            body = body,
            metadata = metadata)
        results[index] = article_object.__dict__

    import json
    with open('./test.json', 'w') as outf:
        json.dump(results, outf, indent=4)