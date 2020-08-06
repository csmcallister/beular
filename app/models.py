import re

import contractions
import eli5
from eli5.formatters import format_as_html
from eli5.formatters.as_dict import format_as_dict
import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import textract

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


def predict(lines, current_app):
    estimator = current_app.config['ESTIMATOR']
    clean_lines = [clean_text(line) for line in lines]
    explanations = []
    y_preds = []
    y_probs = []
    for clean_line in clean_lines:
        expl = eli5.explain_prediction(
            estimator.steps[-1][1],
            clean_line,
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
        if len(clean_line.split()) < 3:
            # one or two words can't be non-compliant
            y_pred = 0
            y_prob = 1.0
        y_preds.append(y_pred)
        y_probs.append(y_prob)
    y_probs = [f'{round(y_prob, 3) * 100}%' for y_prob in y_probs]
    data = zip(y_preds, lines, clean_lines, y_probs, explanations)
    results = [
        dict(
            y_pred=y, line=l, clean_line=cl, y_prob=y_prob, expl=expl
        ) for y, l, cl, y_prob, expl in data
    ]
    return results


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

def read_doc(doc_path):
    """Textract a doc given its path
    
    Arguments:
        file_name {str} -- path to a doc
    """    
    if doc_path.endswith('pdf'):
        # return parse_tesseract(doc_path)
        return parse_pdfminer(doc_path)
    else:  
        b_text = textract.process(doc_path, encoding='utf-8', errors='ignore')
        text = b_text.decode('utf8', errors='ignore').strip()
        return re.sub("\n+", "\n", text)
