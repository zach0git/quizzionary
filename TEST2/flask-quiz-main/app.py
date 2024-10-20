from flask import Flask, render_template, request, redirect, session, flash
from datetime import datetime, timedelta
import pytz  # Import the pytz library

app = Flask(__name__)
app.secret_key = 'your_secret_key'

from questions import questions

# Add a constant for the quiz duration (in seconds)
QUIZ_DURATION_SECONDS = 3000  # Adjust the duration as needed

@app.route('/')
def index():
    return render_template('index.html', categories=list(questions.keys()))

@app.route('/quiz', methods=['POST', 'GET'])
def quiz():
    if request.method == 'POST':
        category = request.form.get('category')
        if category:
            session['category'] = category
            session['score'] = 0
            session['question_index'] = 0
            # Store the start time of the quiz
            session['quiz_start_time'] = datetime.now()
            # Pass the end time of the quiz to the template
            session['quiz_end_time'] = session['quiz_start_time'] + timedelta(seconds=QUIZ_DURATION_SECONDS)
            return redirect('/question')
    return redirect('/')

@app.route('/question', methods=['GET', 'POST'])
def question():
    category = session.get('category')
    score = session.get('score')
    question_index = session.get('question_index')

    # Check if the quiz duration has exceeded
    if 'quiz_start_time' in session:
        # Use pytz to make datetime.now() offset-aware
        now = datetime.now(pytz.utc)
        elapsed_time = now - session['quiz_start_time']
        if elapsed_time.total_seconds() > QUIZ_DURATION_SECONDS:
            flash('Time is up! Quiz has ended.')
            return redirect('/result')

    if category and score is not None and question_index is not None:
        if request.method == 'POST':
            user_answer = request.form.get('answer')
            if user_answer and user_answer == questions[category][question_index]['answer']:
                session['score'] += 1

            session['question_index'] += 1
            if session['question_index'] < len(questions[category]):
                return redirect('/question')
            else:
                return redirect('/result')

        current_question = questions[category][question_index]
        return render_template('quiz.html', category=category, question=current_question, index=question_index + 1, total=len(questions[category]))

    return redirect('/')
@app.route('/result')
def result():
    category = session.get('category')
    score = session.get('score')
    if category and score is not None:
        # Calculate the total time taken for the quiz
        if 'quiz_start_time' in session:
            # Use pytz to make datetime.now() offset-aware
            now = datetime.now(pytz.utc)
            total_time_taken = now - session['quiz_start_time']
        else:
            total_time_taken = timedelta(seconds=0)

        return render_template('result.html', category=category, score=score, total=len(questions[category]), total_time_taken=total_time_taken)
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)
