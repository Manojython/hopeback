from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.models import model_from_json, load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import string
import nltk
import tensorflow as tf

def models():
    with open('tokenizer.json') as f:
        tokenizer = tokenizer_from_json(f.read())

    with open('model_architecture.json', 'r') as f:
        model = model_from_json(f.read())

    # Load weights into the new model
    model.load_weights('model_weights.h5')

    return model, tokenizer

model, tokens = models()


def clean_text(text):
    text = text.lower()                                 
    text =  re.sub(r'@\S+', '',text)                     
    text =  re.sub(r'http\S+', '',text)                  
    text =  re.sub(r'pic.\S+', '',text) 
    text =  re.sub(r"[^a-zA-Z+']", ' ',text)            
    text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text+' ')     
    text = "".join([i for i in text if i not in string.punctuation])
    words = nltk.tokenize.word_tokenize(text)
    stopwords = nltk.corpus.stopwords.words('english')   
    text = " ".join([i for i in words if i not in stopwords and len(i)>2])
    text= re.sub("\s[\s]+", " ",text).strip()            
    return text


def predict(text):
    x_test = pad_sequences(tokens.texts_to_sequences([text]), maxlen=157)
 
    score = model.predict([x_test])[0]
    tf.keras.backend.clear_session()
    return {"score": float(score)}  

print(predict(clean_text('#usNWSgov Severe Weather Statement issued August 05 at 10:38PM EDT by NWS: ...THE SEVERE THUNDERSTORM WARNING ... http://t.co/EpzgG4uqJI')))
print(predict(clean_text('[HIGH PRIORITY] SEVERE THUNDERSTORM WATCH ENDED Issued for Lethbridge [Updated: Aug 05th 20:29 MDT] http://t.co/yqYiwjN8eZ')))
print(predict(clean_text('Beautiful lightning as seen from plane window http://t.co/5CwUyLnFUm http://t.co/1tyYqFz13D')))



# app = Flask(__name__)

# @app.route("/")
# def index():
#     return "Hello World!"

# @app.route('/prediction',methods=['POST','GET'])
# def getPrediction():
#     if request.method == 'POST':
#       sentence = request.form['text']
#       score = (predict(clean_text(sentence)))
#       print(score)
#       return str(round(score['score']))
# if __name__ == '__main__':
#     app.run(debug=True)