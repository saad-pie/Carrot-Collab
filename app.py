from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

def split_topic_into_subtopics(topic):
    # Placeholder: Replace with LLM logic
    return [f"{topic} - Part {i+1}" for i in range(5)]

def generate_script_for_subtopic(subtopic):
    # Placeholder: Replace with LLM logic
    return f"This is a short narration script for: {subtopic}."  # Example script

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

@app.route('/scripts')
def scripts():
    subtopics = session.get('subtopics', [])
    scripts = session.get('scripts', [])
    topic = session.get('topic', '')
    return render_template('scripts.html', topic=topic, subtopics=subtopics, scripts=scripts)

if __name__ == '__main__':
    app.run(debug=True)