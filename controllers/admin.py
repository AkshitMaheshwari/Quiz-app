from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from models.models import db
from models.models import Subject, Chapter, Quiz, Question,Score,QuizResponse,User

admin = Blueprint('admin', __name__)

def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin.route('/admin/dashboard')
@admin_required
def dashboard():
    subjects = Subject.query.all()
    return render_template('admin/dashboard.html', subjects=subjects)

@admin.route('/admin/search', methods=['GET'])
@admin_required
def search():
    query = request.args.get('q', "").strip()
    
    
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()
    users = User.query.filter(User.full_name.ilike(f"%{query}%")).all()
    
    return render_template(
        'admin/search_results.html',
        query=query,
        subjects=subjects,
        chapters=chapters,
        quizzes=quizzes,
        users=users
    )
@admin.route('/admin/quiz/<int:quiz_id>/results')
@admin_required
def quiz_results(quiz_id):
    """Show overall quiz results."""
    quiz = Quiz.query.get_or_404(quiz_id)
    scores = Score.query.filter_by(quiz_id=quiz_id).all()

    total_attempts = len(scores)
    total_score = sum(score.total_scored for score in scores) if total_attempts > 0 else 0
    avg_score = total_score / total_attempts if total_attempts > 0 else 0

    user_results = []
    for score in scores:
        responses = QuizResponse.query.filter_by(score_id=score.id).all()
        user_data = {
            "user": score.user,  
            "total_scored": score.total_scored,
            "correct_answers": score.correct_answers,
            "total_questions": score.total_questions,
            "time_taken": score.time_taken,
            "attempt_time": score.time_stamp_of_attempt,
            "responses": [
                {
                    "question": response.question.question_statement,
                    "selected_option": response.selected_option,
                    "correct_option": response.question.correct_option,
                    "is_correct": response.is_correct
                }
                for response in responses
            ]
        }
        user_results.append(user_data)

    return render_template(
        'admin/quiz_result.html',
        quiz=quiz,
        user_results=user_results,
        total_attempts=total_attempts,
        avg_score=avg_score
    )
@admin.route('/admin/quiz/<int:quiz_id>/user/<int:user_id>/result')
@admin_required
def view_quiz_result(quiz_id, user_id):
    """Show a specific user's results for a quiz."""
    quiz = Quiz.query.get_or_404(quiz_id)
    user = User.query.get_or_404(user_id)
    score = Score.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()

    if not score:
        flash("No result found for this user in the selected quiz.")
        return redirect(url_for('admin.quiz_results', quiz_id=quiz_id))

    responses = QuizResponse.query.filter_by(score_id=score.id).all()

    result_data = []
    for response in responses:
        question = response.question  
        result_data.append({
            "question_text": question.question_statement,
            "options": [question.option1, question.option2, question.option3, question.option4],  # Add options
            "selected_option": response.selected_option,
            "correct_option": question.correct_option
        })

    return render_template('admin/quiz_results.html', quiz=quiz, user=user, score=score, result_data=result_data)

@admin.route('/user/<int:user_id>/scores', methods=['GET'])
def view_user_scores(user_id):
    """Show all quiz scores of a user."""
    user = User.query.get_or_404(user_id)
    scores = Score.query.filter_by(user_id=user_id).all()
    return render_template('admin/user_scores.html', user=user, scores=scores)
@admin.route('/admin/users')
@admin_required
def list_users():
    """Show all registered users"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)


# Subject CRUD

@admin.route('/admin/subjects/new', methods=['GET', 'POST'])
@admin_required
def new_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        
        flash('Subject created successfully!')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/subject_form.html')

@admin.route('/admin/subjects/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    
    if request.method == 'POST':
        subject.name = request.form.get('name')
        subject.description = request.form.get('description')
        db.session.commit()
        
        flash('Subject updated successfully!')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/subject_form.html', subject=subject)

@admin.route('/admin/subjects/<int:id>/delete')
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    
    flash('Subject deleted successfully!')
    return redirect(url_for('admin.dashboard'))

# Chapter CRUD
@admin.route('/admin/subjects/<int:subject_id>/chapters')
@admin_required
def list_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('admin/chapters.html', subject=subject)

@admin.route('/admin/subjects/<int:subject_id>/chapters/new', methods=['GET', 'POST'])
@admin_required
def new_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        
        flash('Chapter created successfully!')
        return redirect(url_for('admin.list_chapters', subject_id=subject_id))
    
    return render_template('admin/chapter_form.html', subject=subject)

@admin.route('/admin/chapters/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    
    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.description = request.form.get('description')
        db.session.commit()
        
        flash('Chapter updated successfully!')
        return redirect(url_for('admin.list_chapters', subject_id=chapter.subject_id))
    
    return render_template('admin/chapter_form.html', chapter=chapter, subject=chapter.subject)

@admin.route('/admin/chapters/<int:id>/delete')
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    
    flash('Chapter deleted successfully!')
    return redirect(url_for('admin.list_chapters', subject_id=subject_id))

# Quiz CRUD

@admin.route('/admin/chapters/<int:chapter_id>/quizzes')
@admin_required
def list_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('admin/quizzes.html', chapter=chapter)

@admin.route('/admin/chapters/<int:chapter_id>/quizzes/new', methods=['GET', 'POST'])
@admin_required
def new_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        time_duration = int(request.form.get('duration_minutes'))
        start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        
        quiz = Quiz(
            title=title,
            time_duration=time_duration,
            start_time=start_time,
            end_time=end_time,
            chapter_id=chapter_id
        )
        db.session.add(quiz)
        db.session.commit()
        
        flash('Quiz created successfully!')
        return redirect(url_for('admin.list_quizzes', chapter_id=chapter_id))
    
    return render_template('admin/quiz_form.html', chapter=chapter)

@admin.route('/admin/quizzes/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    
    if request.method == 'POST':
        quiz.title = request.form.get('title')
        quiz.time_duration = int(request.form.get('duration_minutes'))
        quiz.start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        quiz.end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        db.session.commit()
        
        flash('Quiz updated successfully!')
        return redirect(url_for('admin.list_quizzes', chapter_id=quiz.chapter_id))
    
    return render_template('admin/quiz_form.html', quiz=quiz, chapter=quiz.chapter)

@admin.route('/admin/quizzes/<int:id>/delete')
@admin_required
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    chapter_id = quiz.chapter_id
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz deleted successfully!')
    return redirect(url_for('admin.list_quizzes', chapter_id=chapter_id))

# Question CRUD

@admin.route('/admin/quizzes/<int:quiz_id>/questions')
@admin_required
def list_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('admin/questions.html', quiz=quiz)

@admin.route('/admin/quizzes/<int:quiz_id>/questions/new', methods=['GET', 'POST'])
@admin_required
def new_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        question = Question(
            question_statement=request.form.get('question_statement'),
            option1=request.form.get('option1'),
            option2=request.form.get('option2'),
            option3=request.form.get('option3'),
            option4=request.form.get('option4'),
            correct_option=request.form.get('correct_option'),
            quiz_id=quiz_id
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('Question created successfully!')
        return redirect(url_for('admin.list_questions', quiz_id=quiz_id))
    
    return render_template('admin/question_form.html', quiz=quiz)

@admin.route('/admin/questions/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_question(id):
    question = Question.query.get_or_404(id)
    
    if request.method == 'POST':
        question.question_statement = request.form.get('question_statement')
        question.option1 = request.form.get('option1')
        question.option2 = request.fovbrm.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')
        question.correct_option = request.form.get('correct_option')
        db.session.commit()
        
        flash('Question updated successfully!')
        return redirect(url_for('admin.list_questions', quiz_id=question.quiz_id))
    
    return render_template('admin/question_form.html', question=question, quiz=question.quiz)

@admin.route('/admin/questions/<int:id>/delete')
@admin_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!')
    return redirect(url_for('admin.list_questions', quiz_id=quiz_id))
