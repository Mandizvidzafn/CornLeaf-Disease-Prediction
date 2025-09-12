import os
import tensorflow as tf
import numpy as np
from skimage import io
from keras.utils import load_img, img_to_array
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.applications import ResNet50
from keras.models import load_model
from flask import Flask, redirect, session, url_for, request, render_template
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


def model_predict(img_path, model):
    img = load_img(img_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    preds = model.predict(img_array)
    return preds


@app.route('/', methods=['GET'])
def index():
    return render_template('base.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)
        print(preds[0])

        # x = x.reshape([64, 64]);
        disease_class = ['Pepper__bell___Bacterial_spot', 'Pepper__bell___healthy', 'Potato___Early_blight',
                         'Potato___Late_blight', 'Potato___healthy', 'Tomato_Bacterial_spot', 'Tomato_Early_blight',
                         'Tomato_Late_blight', 'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot',
                         'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato__Target_Spot',
                         'Tomato__Tomato_YellowLeaf__Curl_Virus', 'Tomato__Tomato_mosaic_virus', 'Tomato_healthy']
        a = preds[0]
        ind = np.argmax(a)
        print('Prediction:', disease_class[ind])
        result = disease_class[ind]
        confidence = round(100 * np.max(preds), 2)
        return render_template('result.html', prediction=result, confidence=confidence, image=secure_filename(f.filename))
    return render_template('base.html')


@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('about.html')

@app.route('/recommendations')
def recommendations():
    if 'user' not in session:
        return redirect(url_for('login'))

    predicted_class = session.get('prediction')
    if not predicted_class:
        return redirect(url_for('upload'))

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

    actions = recommended_actions.get(predicted_class, ["No specific recommendations available."])
    return render_template('recommendations.html', predictions=predicted_class, recommendations=actions)



if __name__ == '__main__':
    app.run(debug=True)

   # Serve the app with gevent
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()
