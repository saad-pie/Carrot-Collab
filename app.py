from flask import Flask, render_template, request, redirect, url_for, session
import os
from diffusers import StableDiffusionXLPipeline
import torch
from PIL import Image
import io
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load SDXL pipeline once (on CPU)
sdxl_pipe = None
def get_sdxl_pipe():
    global sdxl_pipe
    if sdxl_pipe is None:
        sdxl_pipe = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float32
        ).to("cpu")
    return sdxl_pipe

def split_topic_into_subtopics(topic):
    # Placeholder: Replace with LLM logic
    return [f"{topic} - Part {i+1}" for i in range(5)]

def generate_script_for_subtopic(subtopic):
    # Placeholder: Replace with LLM logic
    return f"This is a short narration script for: {subtopic}."  # Example script

def generate_image_for_script(script):
    # Use SDXL to generate an image from the script prompt
    pipe = get_sdxl_pipe()
    prompt = script
    image = pipe(prompt=prompt, num_inference_steps=20).images[0]
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    img_bytes = buf.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_b64

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        topic = request.form.get('topic')
        subtopics = split_topic_into_subtopics(topic)
        session['subtopics'] = subtopics
        session['topic'] = topic
        return redirect(url_for('subtopics'))
    return render_template('index.html')

@app.route('/subtopics', methods=['GET', 'POST'])
def subtopics():
    subtopics = session.get('subtopics', [])
    topic = session.get('topic', '')
    if request.method == 'POST':
        # Generate scripts for each subtopic
        scripts = [generate_script_for_subtopic(st) for st in subtopics]
        session['scripts'] = scripts
        return redirect(url_for('scripts'))
    return render_template('subtopics.html', topic=topic, subtopics=subtopics)

@app.route('/scripts', methods=['GET', 'POST'])
def scripts():
    subtopics = session.get('subtopics', [])
    scripts = session.get('scripts', [])
    topic = session.get('topic', '')
    if request.method == 'POST':
        # Generate images for each script
        images = [generate_image_for_script(sc) for sc in scripts]
        session['images'] = images
        return redirect(url_for('images'))
    return render_template('scripts.html', topic=topic, subtopics=subtopics, scripts=scripts)

@app.route('/images')
def images():
    subtopics = session.get('subtopics', [])
    scripts = session.get('scripts', [])
    images = session.get('images', [])
    topic = session.get('topic', '')
    return render_template('images.html', topic=topic, subtopics=subtopics, scripts=scripts, images=images)

if __name__ == '__main__':
    app.run(debug=True)