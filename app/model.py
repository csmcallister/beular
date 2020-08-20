import asyncio
import base64
import re

import aiohttp
import async_timeout
import contractions
import eli5
from eli5.formatters import format_as_html
from eli5.formatters.as_dict import format_as_dict
import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import numpy as np
import requests
from sklearn import metrics
import textract


loop = asyncio.get_event_loop()

clause_regex = re.compile((
    r'(\n\s{0,}('
    r'([i,l,v,I,V,x,X]{1,}[\.,])|'
    r'(\(\d{1,}\))|'
    r'([A-z]{1}\.)|'
    r'([A-z]{1}\))|'
    r'(\d{1,}[\.,]\d{0,}\.{0,1})|'
    r'(e)|'
    r'(\([A-z]\))'
    r')\s{1,})'
))

page_regex = re.compile(r"page \d of \d")

stopwords = {
    'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there',
    'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they',
    'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into',
    'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who',
    'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below',
    'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me',
    'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our',
    'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she',
    'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and',
    'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then',
    'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not',
    'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where',
    'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few',
    'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by',
    'doing', 'it', 'how', 'further', 'was', 'here', 'than'
}


async def fetch(url, data):
    async with aiohttp.ClientSession() as session, async_timeout.timeout(10):
        async with session.post(url, data=data) as response:
            return await response.json()


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    elif treebank_tag == 'PRP':
        return wordnet.ADJ_SAT
    elif treebank_tag == 'MD':
        return 'n'
    else:
        return ''


def clean_text(text):
    """
    Lemmatize, lowercase, alpha-only and b/w 3 and 17 chars long
    
    Parameters:
        doc (str): the text of a clause
        
    Returns:
        words (str): a string of space-delimited lower-case alpha-only words
    """
    no_nonsense_re = re.compile(r'^[a-zA-Z]+$')
    text = contractions.fix(text, slang=False)
    lemmatizer = WordNetLemmatizer() 
    tagged_tokens = nltk.pos_tag(word_tokenize(text))
    words = ''
    for token, pos in tagged_tokens:
        wordnet_pos = get_wordnet_pos(pos)
        if wordnet_pos:
            lemma = lemmatizer.lemmatize(token.lower(), pos=wordnet_pos)
            if re.match(no_nonsense_re, lemma):
                words += f' {lemma}'
    
    return words.strip()


def gen_html(token_to_sim, y_pred, y_prob):
    elems = ''

    for token, sim in token_to_sim:
        sim = sim[0][0]
        opacity = np.clip(abs(sim), .5, 1)
        hue = 0 if sim < 0 else 120
        light = np.clip(round(1 - abs(sim), 2) * 100, 50, 97)
        
        elem = (
            f'<span style="background-color: hsl({hue}, 100.00%, {light}%);'
            f' opacity: {opacity}" title="{sim}">{token}</span>'
        )
        
        elems += elem + ' '
    p = "Compliant" if y_pred == 0 else "NonCompliant"

    y_prob = f'{round(np.clip(y_prob, 0, 1), 3) * 100}%'
    html_expl = f"<p>Predicted as {p}, with a probability of {y_prob}.</p>"
    html_expl += elems
    
    return html_expl


def token_to_cosine_sim(tokens, mean_vec, estimator, current_app):
    token_to_sim = []
    for token in tokens:
        
        token_vec = estimator.get_word_vector(token).reshape(1, -1)
        
        sim = metrics.pairwise.cosine_similarity(
            mean_vec.reshape(1, -1),
            token_vec   
        )
        
        token_to_sim.append((token, sim))

    return token_to_sim


def explain_bt(pred, prob, tokens, mean_vec, current_app, estimator):
    token_to_sim = token_to_cosine_sim(
        tokens.split(),
        mean_vec,
        estimator,
        current_app
    )

    html_expl = gen_html(token_to_sim, pred, prob)
    return html_expl


def bt_predict(lines, current_app):    
    mean_vec = current_app.config['MEAN_VEC']
    estimator = current_app.config['ESTIMATOR']
    
    explanations = []
    y_preds = []
    y_probs = []
    for line in lines:
        if not line.strip():
            continue
        tokens = ' '.join(nltk.word_tokenize(line.lower()))
        pred, prob = estimator.predict(tokens)
        pred = int(pred[0][-1])
        prob = prob[0]
        html_expl = explain_bt(
            pred,
            prob,
            tokens,
            mean_vec,
            current_app,
            estimator
        )
        explanations.append(html_expl)
        y_preds.append(pred)
        
        y_probs.append(f'{round(prob, 3) * 100}%')
    
    data = zip(y_preds, lines, lines, y_probs, explanations)
    results = [
        dict(
            y_pred=y, line=l, clean_line=cl, y_prob=y_prob, expl=expl
        ) for y, l, cl, y_prob, expl in data
    ]
    
    return results


def sklearn_predict(lines, current_app):
    estimator = current_app.config['ESTIMATOR']
    explanations = []
    y_preds = []
    y_probs = []
    for line in lines:
        line = ' '.join(t for t in line.split() if t not in stopwords)
        if not line.strip():
            continue
        expl = eli5.explain_prediction(
            estimator.steps[-1][1],
            line,
            estimator.steps[0][1],
            target_names=['Compliant', 'Not Compliant'],
            top=10
        )
        html_explanation = format_as_html(
            expl,
            force_weights=False,
            show_feature_values=True
        ).replace("\n", "").strip()
        explanations.append(html_explanation)
        expl_dict = format_as_dict(expl)
        targets = expl_dict['targets'][0]
        target = targets['target']
        y_pred = 1 if target.startswith('N') else 0
        y_prob = targets['proba']
        if len(line.split()) < 3:
            # one or two words can't be non-compliant
            y_pred = 0
            y_prob = 1.0
        y_preds.append(y_pred)
        y_probs.append(y_prob)
    y_probs = [f'{round(y_prob, 3) * 100}%' for y_prob in y_probs]
    data = zip(y_preds, lines, lines, y_probs, explanations)
    results = [
        dict(
            y_pred=y, line=l, clean_line=cl, y_prob=y_prob, expl=expl
        ) for y, l, cl, y_prob, expl in data
    ]
    return results


def sklearn_api_predict(lines, current_app):
    uri = current_app.config['MODEL_URI']
    y_preds = []
    y_probs = []
    explanations = []
    
    
    async_data = [l.replace(",", "").replace("\n", "").encode(encoding='utf-8') for l in lines]
    tasks = [fetch(uri, data=d) for d in async_data]
    responses = loop.run_until_complete(asyncio.gather(*tasks))

    for i, r in enumerate(responses):
        data = r[0]
        y_preds.append(int(data.get('prediction')))
        y_probs.append(data.get('pred_prob'))
        base64_expl_bytes = data.get('expl').encode('utf-8')
        expl = base64.b64decode(base64_expl_bytes).decode('utf-8')
        explanations.append(expl)
    
    data = zip(y_preds, lines, lines, y_probs, explanations)
    results = [
        dict(
            y_pred=y, line=l, clean_line=cl, y_prob=y_prob, expl=expl
        ) for y, l, cl, y_prob, expl in data
    ]
    
    # for line in lines:
    #     # model wants csv content, so prevent issues
    #     line = line.replace(",", "").replace("\n", "")
    #     r = requests.post(uri, data=line.encode(encoding='utf-8'))
    #     data = r.json()[0]
    #     y_preds.append(int(data.get('prediction')))
    #     y_probs.append(data.get('pred_prob'))
    #     base64_expl_bytes = data.get('expl').encode('utf-8')
    #     expl = base64.b64decode(base64_expl_bytes).decode('utf-8')
    #     explanations.append(expl)
    # data = zip(y_preds, lines, lines, y_probs, explanations)
    # results = [
    #     dict(
    #         y_pred=y, line=l, clean_line=cl, y_prob=y_prob, expl=expl
    #     ) for y, l, cl, y_prob, expl in data
    # ]
    return results


def bt_api_predict(lines, current_app):
    mean_vec = current_app.config['MEAN_VEC']
    estimator = current_app.config['ESTIMATOR']
    
    uri = current_app.config['MODEL_URI']
    payload = {'instances': []}
    for line in lines:
        if not line.strip():
            continue
        line = " ".join(nltk.word_tokenize(line))
        payload['instances'].append(line)
    r = requests.post(uri, json=payload)
    data = r.json()

    explanations = []
    y_preds = []
    y_probs = []
    for i, d in enumerate(data):
        pred = int(d['label'][0][-1])
        prob = np.clip(d['prob'][0], 0, 1)
        tokens = payload['instances'][i]
        html_expl = explain_bt(
            pred,
            prob,
            tokens,
            mean_vec,
            current_app,
            estimator
        )
        explanations.append(html_expl)
        y_preds.append(pred)
        y_probs.append(y_probs)

    data = zip(y_preds, lines, lines, y_probs, explanations)
    results = [
        dict(
            y_pred=y, line=l, clean_line=cl, y_prob=y_prob, expl=expl
        ) for y, l, cl, y_prob, expl in data
    ]

    return results
    

def api_predict(lines, current_app):
    if current_app.config['BT']:
        return bt_api_predict(lines, current_app)
    else:
        return sklearn_api_predict(lines, current_app)


def predict(lines, current_app):
    if current_app.config['MODEL_URI']:
        return api_predict(lines, current_app)
    else:
        if current_app.config['BT']:
            return bt_predict(lines, current_app)
        else:
            return sklearn_predict(lines, current_app)
    

def parse_pdfminer(doc_path):
    b_text = textract.process(
        doc_path,
        method='pdftotext',
        encoding='utf_8',
        errors='ignore'
    )
    text = b_text.decode('utf8', errors='ignore').strip()
    
    formatted_clauses = []
    clauses = re.split(clause_regex, re.sub(r'  +', '', text))
    clauses = [c for c in clauses if c]
    for i, c in enumerate(clauses):
        c = c.strip()
        if not c or len(c) < 3:
            continue
        elif len(c.split(" ")) < 3:
            continue
        if i % 2 == 0:
            clause = re.sub(r"\n+", " ", c)
            
            if clause[0].islower():
                # this is not the start of a clause
                # so append to previous
                formatted_clauses[-1] += ' ' + clause
            else:
                # this is the start of the clause
                # so prepend with clause id
                if i == 0:
                    formatted_clauses.append(clause)
                else:
                    clause = clauses[i - 1] + ' ' + clause
                    formatted_clauses.append(clause)

    clauses = []
    for c in formatted_clauses:
        c = re.sub(r'\n', ' ', c)
        if not c.strip() or len(c) < 3:
            continue
        elif len(c.split(" ")) < 3:
            continue
        clauses.append(c)

    return "\n".join(clauses)     


def parse_word_doc(doc_path):
    b_text = textract.process(doc_path, encoding='utf-8', errors='ignore')
    text = b_text.decode('utf8', errors='ignore').strip()
    text = re.sub("\n+", "\n", text)
    
    parsed_clauses = []
    for clause in text.split("\n"):
        clause = clause.strip()
        if "<<" in clause or clause.startswith("%"):
            continue
        elif len(clause.split()) <= 2 or clause.endswith(">"):
            continue
        elif len(clause.split()) <= 10 and clause.endswith(":"):
            continue
        elif all(c.isupper() for c in clause):
            continue
        elif clause.lower() == "company end user license master agreement":
            continue
        elif page_regex.findall(clause.lower()):
            continue
        else:
            parsed_clauses.append(clause)
    
    clauses = []
    for clause in parsed_clauses:
        if clause[0].islower() or clause.startswith(("(", "U.S.C")):
            # this is the continuation of the previous clause
            clauses[-1] += f' {clause}'
        else:
            clauses.append(clause)

    return "\n".join(clauses)


def read_doc(doc_path):
    """Textract a doc given its path
    
    Arguments:
        file_name {str} -- path to a doc
    """    
    if doc_path.endswith('pdf'):
        return parse_pdfminer(doc_path)
    else:  
        return parse_word_doc(doc_path)
