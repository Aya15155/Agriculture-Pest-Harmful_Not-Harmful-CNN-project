from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import io
from PIL import Image
import os
from fastapi.middleware.cors import CORSMiddleware
import h5py  # Import h5py for inspecting HDF5 files

app = FastAPI()

# Load the trained model
MODEL_PATH = os.path.join(os.getcwd(), "pest_cnn_dual_output.h5")
print(f"Model Path: {MODEL_PATH}")  # Correctly format the print statement

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust the frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if model exists at the specified path
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Ensure the file is in the correct directory.")

# Use h5py to inspect the .h5 file before loading it
try:
    with h5py.File("MODEL_PATH", 'r') as file:
        # Print the structure of the file to check if it's a valid HDF5 file
        print("HDF5 File Structure:")
        for key in file.keys():
            print(f"Key: {key}, Type: {type(file[key])}")
except Exception as e:
    raise RuntimeError(f"Failed to open the .h5 file: {e}")

# Try to load the model using Keras
try:
    model = load_model(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")

# Define class labels (Update with actual insect categories)
class_labels = ["Africanized Honey Bees (Killer Bees)", "Insect B", "Insect C"]  # Replace with actual class names
harmful_classes = [0]  # Example: Index 0 = Harmful

def preprocess_image(img):
    """Prepares the image for model prediction."""
    img = img.resize((224, 224))
    img_array = image.img_to_array(img) / 255.0  # Normalize the image
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    """Handles image upload and returns predictions."""
    try:
        # Read the uploaded image file
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")  # Ensure RGB mode
        img_array = preprocess_image(img)

        # Get predictions from the model
        insect_pred, harmful_pred = model.predict(img_array)
        insect_index = np.argmax(insect_pred)  # Get the index of the highest prediction for the insect
        harmful_prob = float(harmful_pred[0][0])  # Get harmful probability (assuming binary classification)

        # Determine insect name based on the prediction
        insect_name = class_labels[insect_index]
        is_harmful = harmful_prob > 0.5  # Threshold to classify as harmful

        # Define possible solutions (modify based on your actual insect types)
        solutions = {
            "Africanized Honey Bees (Killer Bees)": "Use organic pesticides.",
            "Insect B": "Keep plants indoors during peak seasons.",
            "Insect C": "Install protective nets."
        }
        solution = solutions.get(insect_name, "No specific solution available.")

        # Return the prediction results
        return {
            "insect": insect_name,
            "harmful_probability": harmful_prob,
            "is_harmful": is_harmful,
            "solution": solution if is_harmful else "Not harmful, no action needed."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
