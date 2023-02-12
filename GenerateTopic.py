import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag

def generate_topic(response: str) -> str:
    words = word_tokenize(response)
    tagged_words = pos_tag(words)
    keywords = [word for word, pos in tagged_words if pos in ['NN', 'NNS', 'NNP', 'NNPS']]
    topic = " ".join(keywords)
    return topic

bot_response = "Tell about advantages of Java."
topic = generate_topic(bot_response)
print("Conversation Topic:", topic)