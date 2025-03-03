import React, { useState } from "react";
import axios from "axios";

function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!image) {
      alert("Please select an image first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", image);

    try {
      const response = await axios.post("http://127.0.0.1:8000/predict/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      

      setResult(response.data);
    } catch (error) {
      console.error("Error uploading image", error);
      alert("Error uploading image. Please try again.");
    }
  };

  return (
    <div style={{ backgroundColor: "#f0f0f0", minHeight: "100vh", padding: "20px" }}>
      <div
        style={{
          display: "flex",
          maxWidth: "800px",
          margin: "auto",
          backgroundColor: "#fff",
          padding: "20px",
          borderRadius: "10px",
          boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.1)",
        }}
      >
        {/* Upload Section */}
        <div style={{ width: "40%", paddingRight: "20px" }}>
          <h3>Upload Insect Image</h3>
          <input type="file" accept="image/*" onChange={handleImageChange} style={{ marginBottom: "10px" }} />
          <button
            onClick={handleSubmit}
            style={{
              backgroundColor: "#007bff",
              color: "#fff",
              border: "none",
              padding: "10px 15px",
              borderRadius: "5px",
              cursor: "pointer",
              fontSize: "16px",
            }}
          >
            Submit
          </button>
        </div>

        {/* Separator Line */}
        <div style={{ width: "2px", backgroundColor: "#ddd", height: "100%", margin: "0 20px" }}></div>

        {/* Results Section */}
        <div style={{ width: "58%" }}>
          {result ? (
            <div>
              <h3 style={{ color: "#333", borderBottom: "2px solid #ddd", paddingBottom: "5px" }}>Prediction Result</h3>
              <p><strong>Insect Type:</strong> {result.insect}</p>
              <p><strong>Harmful Probability:</strong> {result.harmful_probability * 100}%</p>
              <p><strong>Is Harmful:</strong> {result.is_harmful ? "Yes" : "No"}</p>
              <p><strong>Solution:</strong> {result.solution}</p>
            </div>
          ) : (
            <p style={{ color: "#888" }}>No result yet. Upload an image to see predictions.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
