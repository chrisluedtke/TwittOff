from collections import OrderedDict

from numpy import array, ones, zeros, vstack, concatenate
from sklearn.linear_model import LogisticRegression

from .models import User
from .twitter import BASILICA


def predict_user(user1_name, user2_name, tweet_text):
    user1 = User.query.filter(User.name == user1_name).one()
    user2 = User.query.filter(User.name == user2_name).one()
    user1_embeddings = array([tweet.embedding for tweet in user1.tweets])
    user2_embeddings = array([tweet.embedding for tweet in user2.tweets])
    user1_labels = ones(len(user1.tweets))
    user2_labels = zeros(len(user2.tweets))

    embeddings = vstack([user1_embeddings, user2_embeddings])
    labels = concatenate([user1_labels, user2_labels])

    log_reg = LogisticRegression(solver='lbfgs', max_iter=1000)
    log_reg.fit(embeddings, labels)

    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    result = log_reg.predict_proba(array(tweet_embedding).reshape(1, -1))[0]
    result = {user1_name: round(result[0] * 100, 1), 
              user2_name: round(result[1] * 100, 1)}
    result = OrderedDict(sorted(result.items(), key=lambda kv: kv[1], 
                                reverse=True))

    return result
