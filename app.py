from flask import Flask, request, render_template

#from lib.db_lib import DataBase

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('sub_pages/about.html')

@app.route('/experience')
def work_experience():
    """
    db = DataBase('experience')
    job_data = db.get_experience()
    print(job_data)
    """
    return render_template('sub_pages/experience.html')

@app.route('/projects')
def projects():
    return render_template('sub_pages/projects.html')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('sub_pages/404.html'), 404