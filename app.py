
import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import yaml

app = Flask(__name__)

# Dictionary to map class names to Korean descriptions
KOREAN_DESCRIPTIONS = {
    'cat_sitting': '앉아있을 거에요',
    'cat_eating': '뭔가를 먹고 있을 거에요',
    'cat_lying': '뒹굴거리고 있을 거에요',
    'cat_sleeping': '꿈나라로 갔을 거에요',
    'cat_standing': '서 있을 거에요',
    'cat_yawning': '졸릴 거에요'
}

# Load YOLO model
model = YOLO('best.pt')

# Load class names from data.yaml
with open('data.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
    class_names = data['names']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('static/uploads', filename)
        file.save(filepath)

        # Run inference
        results = model(filepath)

        # Process results
        predictions = []
        annotated_filename = None
        if results:
            r = results[0]  # Get the first result

            # Save the annotated image
            annotated_filename = f"predicted_{filename}"
            annotated_filepath = os.path.join('static/uploads', annotated_filename)
            r.save(filename=annotated_filepath)

            # Extract predictions for each detected box
            for box in r.boxes:
                class_id = int(box.cls[0])
                class_name = class_names[class_id]
                confidence = float(box.conf[0])

                # Get Korean description and format the output string
                description = KOREAN_DESCRIPTIONS.get(class_name, "알 수 없는 행동을 하고 있어요") # Default message
                confidence_percent = int(confidence * 100)
                prediction_string = f"{confidence_percent}% 확률로 {description}."
                predictions.append(prediction_string)

        return render_template('index.html', filename=annotated_filename, predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True)
