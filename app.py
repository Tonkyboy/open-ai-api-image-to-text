import os
import base64
from flask import Flask, render_template, request
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
openai_api_key = os.getenv("OPENAI_API_KEY")

# Ensure the directory for saving images exists
IMAGE_UPLOAD_PATH = os.path.join('static', 'images')
if not os.path.exists(IMAGE_UPLOAD_PATH):
    os.makedirs(IMAGE_UPLOAD_PATH)

# OpenAI Client initialization
def initialize_openai_client():
    return openai.OpenAI(api_key=openai_api_key)

# Function to encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Route to render the upload form and handle image and prompt submission
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form.get("prompt")  # Single input field for prompt
        
        image = request.files["image"]
        
        # Save uploaded image to static/images directory
        image_path = os.path.join(IMAGE_UPLOAD_PATH, image.filename)
        image.save(image_path)

        # Encode the image in base64
        base64_image = encode_image(image_path)

        # Initialize OpenAI client
        client = initialize_openai_client()

        try:
            # Create chat completion request
            chat_completion = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt  # Combining prompt and question into one field
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                        ]
                    }
                ]
            )
            # Get response content
            response_text = chat_completion.choices[0].message.content
            return render_template("index.html", response_text=response_text)

        except Exception as e:
            error_message = f"An error occurred: {e}"
            return render_template("index.html", error_message=error_message)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
