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
        y_probs.append(expl_dict['targets'][0]['proba'])
        y_preds.append(expl_dict['targets'][0]['target'])
    y_probs = [f'{round(y_prob, 3) * 100}%' for y_prob in y_probs]
    data = zip(y_preds, lines, clean_lines, y_probs, explanations)
    results = [
        dict(
            y_pred=y, line=l, clean_line=cl, y_prob=y_prob, expl=expl
        ) for y, l, cl, y_prob, expl in data
    ]
    return results


def read_doc(doc_path):
    """Textract a doc given its path
    
    Arguments:
        file_name {str} -- path to a doc
    """
    b_text = textract.process(doc_path, encoding='utf-8', errors='ignore')
    if b_text:
        text = b_text.decode('utf8', errors='ignore').strip() 
    else:
        text = "this is the doc text\nand another clause"
    text = re.sub("\n+", "\n", text)
    return text