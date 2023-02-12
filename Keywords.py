import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk

conversation = "C# is a modern, object-oriented programming language developed by Microsoft to be used with the .NET framework. It is similar to C and C++ in syntax, but provides many additional features and capabilities such as garbage collection, memory management, enhanced type safety, simplified deployment, and improved security."
words = word_tokenize(conversation)
tagged_words = pos_tag(words)

# Extracting keywords using POS tagging
keywords = [word for word, pos in tagged_words if pos in ['NN', 'NNS', 'NNP', 'NNPS']]

# Extracting keywords using NER
tree = ne_chunk(tagged_words)
keywords.extend([tree[0] for tree in tree if hasattr(tree, 'label') and tree.label() == 'GPE'])
print("Keywords:", keywords)
