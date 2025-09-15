import os
from PIL import Image
import tensorflow as tf
import numpy as np
from skimage import io
from keras.utils import load_img, img_to_array
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.applications import ResNet50
from keras.models import load_model
from flask import Flask, jsonify, redirect, session, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

# Define a flask app
app = Flask(__name__)
app.secret_key = "corn_disease_prediction"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db = SQLAlchemy(app)

# Load the model
model = load_model('model/plant_disease_model.h5')
print('Model loaded. Check http://127.0.0.1:5000/')

recommended_actions = {
    "Blight": [
        "Remove and destroy infected leaves to reduce spread.",
        "Apply copper-based fungicides during early symptoms.",
        "Practice crop rotation to avoid recurrent infections.",
        "Ensure adequate spacing to improve air circulation."
    ],
    "Common Rust": [
        "Use resistant maize hybrids if available.",
        "Apply appropriate fungicides such as triazoles.",
        "Plant early to reduce rust development time.",
        "Avoid overhead irrigation to limit moisture."
    ],
    "Gray Leaf Spot": [
        "Plant disease-resistant corn varieties.",
        "Rotate with non-host crops like soybeans.",
        "Apply fungicide before tasseling if high humidity is expected.",
        "Remove and destroy crop residue after harvest."
    ],
    "Healthy": [
        "Maintain optimal watering and fertilization schedules.",
        "Monitor leaves regularly for early signs of disease.",
        "Apply preventive fungicide if disease pressure is high in your area.",
        "Practice good field sanitation."
    ]
}

def model_predict(img_path, model):
    """
    Make a prediction on a single image.
    Use when the image is saved on disk.
    1. Load the image from disk
    2. Preprocess the image to required size
    3. Predict the class of the image
    4. Return the prediction
    """
    img = load_img(img_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    preds = model.predict(img_array)
    return preds

def model_predict_array(img_array, model):
    """
    Make a prediction on a single image array.
    Use when the image is in memory as a numpy array.
    """
    #Make image have 3 channels (RGB) by removing alpha channel if present (RGBA)
    if img_array.shape[-1] == 4:  
        img_array = img_array[..., :3]

    if len(img_array.shape) == 3:  
        img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    preds = model.predict(img_array)
    return preds

@app.route('/', methods=['GET'])
def index():
    session.clear() 
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        #Uncomment to save file to disk
        # Save the file to ./uploads
        #basepath = os.path.dirname(__file__)
        #file_path = os.path.join(
        #    basepath, 'uploads', secure_filename(f.filename))
        #f.save(file_path)

        # Open image in memory
        img = Image.open(f.stream)  

        # Preprocess the image for your model
        img = img.resize((224, 224))   
        img_array = np.array(img) / 255.0 
        img_array = np.expand_dims(img_array, axis=0) 

        # Make prediction
        #preds = model_predict(file_path, model)
        preds = model_predict_array(img_array, model)
        print(preds[0])

        disease_class = ['Blight', 'Common Rust', 'Gray Leaf Spot', 'Healthy']
        a = preds[0]
        ind = np.argmax(a)
        print('Prediction:', disease_class[ind])
        result = disease_class[ind]
        confidence = float(round(100 * np.max(preds[0]), 2))
        actions = [str(rec) for rec in recommended_actions.get(result, ["No specific recommendations available."])]
        print("Confidence: ", confidence)
        print("Recommended Actions: ", actions)
        session['prediction'] = str(result)
        session['confidence'] = confidence
        session['recommendations'] = actions
    return jsonify({
        "prediction": result,
        "confidence": confidence,
        "recommendations": actions,
    })

@app.route('/recommendations')
def recommendations():

    recommendations = session.get('recommendations', None)
    prediction= session.get('prediction', None)
    confidence= session.get('confidence', None)

    return render_template('recommendations.html', prediction=prediction, recommendations=recommendations, confidence=confidence)

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

   # Serve the app with gevent
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()
