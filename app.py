from flask import Flask, render_template, request, redirect, url_for, session
import os
from diffusers import StableDiffusionXLPipeline
# from diffusers import StableVideoDiffusionPipeline  # Uncomment when implementing real SVD
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

# Placeholder for SVD pipeline
def generate_video_for_image(image_b64):
    # Placeholder: Replace with SVD logic
    # For now, just return the image as a static video (mp4) using moviepy
    from moviepy.editor import ImageClip
    import tempfile
    import shutil
    import os
    img_bytes = base64.b64decode(image_b64)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img_file:
        img_file.write(img_bytes)
        img_path = img_file.name
    video_path = img_path.replace('.png', '.mp4')
    clip = ImageClip(img_path).set_duration(2).set_fps(24)
    clip.write_videofile(video_path, codec='libx264', audio=False, verbose=False, logger=None)
    with open(video_path, 'rb') as f:
        video_bytes = f.read()
    video_b64 = base64.b64encode(video_bytes).decode('utf-8')
    # Clean up temp files
    os.remove(img_path)
    os.remove(video_path)
    return video_b64

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

@app.route('/images', methods=['GET', 'POST'])
def images():
    subtopics = session.get('subtopics', [])
    scripts = session.get('scripts', [])
    images = session.get('images', [])
    topic = session.get('topic', '')
    if request.method == 'POST':
        # Generate videos for each image
        videos = [generate_video_for_image(img) for img in images]
        session['videos'] = videos
        return redirect(url_for('videos'))
    return render_template('images.html', topic=topic, subtopics=subtopics, scripts=scripts, images=images)

@app.route('/videos')
def videos():
    subtopics = session.get('subtopics', [])
    scripts = session.get('scripts', [])
    images = session.get('images', [])
    videos = session.get('videos', [])
    topic = session.get('topic', '')
    return render_template('videos.html', topic=topic, subtopics=subtopics, scripts=scripts, images=images, videos=videos)

if __name__ == '__main__':
    app.run(debug=True)