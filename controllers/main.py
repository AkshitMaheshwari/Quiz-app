from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models.models import db
from models.models import Subject, Chapter, Quiz, Question, Score, QuizResponse
from datetime import timezone
from flask import session

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    subjects = Subject.query.all()
    return render_template('main/dashboard.html', subjects=subjects)

@main.route('/search')
def search():
    query = request.args.get('query', '').strip()
    
    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('main.dashboard'))

    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()

    return render_template('main/search_results.html', 
                           query=query, 
                           subjects=subjects, 
                           chapters=chapters, 
                           quizzes=quizzes)

@main.route('/subjects/<int:subject_id>/chapters')
@login_required
def list_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('main/chapters.html', subject=subject)

@main.route('/chapters/<int:chapter_id>/quizzes')
@login_required
def list_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    now = datetime.utcnow()
    return render_template('main/view_quizzes.html', chapter=chapter, current_time=now)

@main.route('/quiz/<int:quiz_id>')
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    quiz_start = quiz.start_time.replace(tzinfo=timezone.utc)
    quiz_end = quiz.end_time.replace(tzinfo=timezone.utc)
    
    
    if now < quiz_start:
        flash('This quiz is not yet available.')
        return redirect(url_for('main.list_quizzes', chapter_id=quiz.chapter_id))
    
    elif now > quiz_end:
        flash('This quiz has ended.')
        return redirect(url_for('main.list_quizzes', chapter_id=quiz.chapter_id))
    
    existing_score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    if existing_score:
        flash('You have already attempted this quiz.')
        return redirect(url_for('main.quiz_result', quiz_id=quiz_id))

    if f'quiz_{quiz_id}_start' not in session:
        session[f'quiz_{quiz_id}_start'] = now.isoformat()

    quiz_duration = quiz.time_duration * 60 
    time_elapsed = (now - datetime.fromisoformat(session[f'quiz_{quiz_id}_start']).replace(tzinfo=timezone.utc)).total_seconds()
    time_remaining = max(0, quiz_duration - int(time_elapsed))

    if time_remaining <= 0:
        return redirect(url_for('main.submit_quiz', quiz_id=quiz_id))

    return render_template('main/quiz.html', quiz=quiz, time_remaining=time_remaining)

@main.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions

    correct_answers = 0
    total_questions = len(questions)

    quiz_score = Score(
        user_id=current_user.id,
        quiz_id=quiz_id,
        total_scored=0,  
        total_questions=total_questions,
        correct_answers=0,
        time_taken=None  
    )
    db.session.add(quiz_score)
    db.session.commit()  

    for question in questions:
        answer = request.form.get(f'question_{question.id}')  
        is_correct = answer == str(question.correct_option)  
        
        quiz_response = QuizResponse(
            score_id=quiz_score.id,
            question_id=question.id,
            selected_option=int(answer) if answer else None,
            is_correct=is_correct
        )
        db.session.add(quiz_response)

        if is_correct:
            correct_answers += 1

    start_time = session.get(f'quiz_{quiz_id}_start')
    time_taken = None
    if start_time:
        start_time = datetime.fromisoformat(start_time).replace(tzinfo=timezone.utc)
        time_taken = int((datetime.utcnow().replace(tzinfo=timezone.utc) - start_time).total_seconds())

    quiz_score.total_scored = correct_answers
    quiz_score.correct_answers = correct_answers
    quiz_score.time_taken = time_taken

    db.session.commit()

    return redirect(url_for('main.quiz_result', quiz_id=quiz_id))

@main.route('/quiz/<int:quiz_id>/result')
@login_required
def quiz_result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()

    if not score:
        flash("You haven't attempted this quiz yet.")
        return redirect(url_for('main.list_quizzes', chapter_id=quiz.chapter_id))

    responses = QuizResponse.query.filter_by(score_id=score.id).all()

    result_data = []
    for response in responses:
        question = Question.query.get(response.question_id)
        result_data.append({
            "question_text": question.question_statement,
            "options": [question.option1, question.option2, question.option3, question.option4],  # All options
            "selected_option": response.selected_option,  
            "correct_option": question.correct_option,
            "is_correct": response.is_correct  
        })

    return render_template('main/quiz_result.html', quiz=quiz, score=score, result_data=result_data)


@main.route('/my_scores')
@login_required
def my_scores():
    scores = Score.query.filter_by(user_id=current_user.id).all()
    return render_template('main/my_scores.html', scores=scores)
