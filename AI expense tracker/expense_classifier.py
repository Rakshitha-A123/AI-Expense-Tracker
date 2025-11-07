from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

# Sample training data
train_texts = [
    "Zomato order payment", "Uber ride payment", "Amazon purchase", 
    "Dominos bill", "IRCTC ticket booking", "Electricity bill payment"
]
train_labels = ["Food", "Travel", "Shopping", "Food", "Travel", "Utilities"]

vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform(train_texts)
model = MultinomialNB()
model.fit(X_train, train_labels)

# Save the model
pickle.dump((vectorizer, model), open("expense_model.pkl", "wb"))

# Function to predict
def predict_category(text):
    vec, mod = pickle.load(open("expense_model.pkl", "rb"))
    x = vec.transform([text])
    return mod.predict(x)[0]
