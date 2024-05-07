from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree


def extract_named_entities(text):
    words = word_tokenize(text)
    tagged_words = pos_tag(words)
    tree = ne_chunk(tagged_words)

    named_entities = []
    for subtree in tree:
        if isinstance(subtree, Tree):
            entity = " ".join([token for token, pos in subtree.leaves()])
            named_entities.append(entity)
    return named_entities
