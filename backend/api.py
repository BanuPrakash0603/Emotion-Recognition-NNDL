from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

model = pickle.load(open('model.pkl', 'rb'))

@app.route("/")
def home():
    return "API is running"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    result = model.predict([list(data.values())])
    return jsonify({"prediction": str(result[0])})

if __name__ == "__main__":
    app.run()