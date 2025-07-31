from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

def split_topic_into_subtopics(topic):
    # Placeholder: Replace with LLM logic
    # For now, just split the topic into 5 example subtopics
    return [f"{topic} - Part {i+1}" for i in range(5)]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        topic = request.form.get('topic')
        subtopics = split_topic_into_subtopics(topic)
        session['subtopics'] = subtopics
        session['topic'] = topic
        return redirect(url_for('subtopics'))
    return render_template('index.html')

@app.route('/subtopics')
def subtopics():
    subtopics = session.get('subtopics', [])
    topic = session.get('topic', '')
    return render_template('subtopics.html', topic=topic, subtopics=subtopics)

if __name__ == '__main__':
    app.run(debug=True)