# app.py - Flask Backend for Prompt Genie

from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Replace with your actual Google Cloud Project ID or leave empty if using environment variable
# The API key should ideally be loaded from environment variables in a production setup
# For Canvas environment, leave it empty as the environment injects it.
# If running locally, you would set this:
# os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
API_KEY = os.environ.get("GEMINI_API_KEY", "") # Keep it empty for Canvas as per instructions

# Define the Gemini API URL
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

@app.route('/')
def index():
    """Renders the main game HTML page."""
    return render_template('index.html')

@app.route('/api/generate_content', methods=['POST'])
def generate_content():
    """
    Endpoint to receive a prompt from the frontend, call the Gemini API,
    and return the AI's response.
    """
    data = request.json
    user_prompt = data.get('prompt')

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ]
        }

        # Add API key to the URL parameters
        api_url_with_key = f"{GEMINI_API_URL}?key={API_KEY}"

        # Make the POST request to the Gemini API
        response = requests.post(api_url_with_key, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        gemini_response = response.json()

        # Extract the text from the AI's response
        if gemini_response and gemini_response.get('candidates'):
            ai_text = gemini_response['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"aiResponse": ai_text})
        else:
            return jsonify({"error": "Invalid response from Gemini API"}), 500

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": f"Failed to get response from AI: {str(e)}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # When running locally, ensure you have a 'templates' folder in the same directory
    # as this app.py, and index.html should be inside it.
    # For Canvas, the structure is managed internally.
    app.run(debug=True) # debug=True for development, set to False for production
