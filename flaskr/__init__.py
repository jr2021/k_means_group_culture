import os
import glob
import sys
import urllib.request
from flask import Flask, flash, g, request, redirect, url_for, render_template, session, url_for, Blueprint
from werkzeug.utils import secure_filename
from k_means import K_Means
from os.path import exists
from speech_recognition import speech_recognize
import json

ALLOWED_EXTENSIONS = {'wav', 'txt'}
##ALLOWED_CLEAN_EXTENSIONS = set(['txt'])
UPLOAD_FOLDER = 'flaskr/DirtyAudio'
UPLOAD_CLEAN_FOLDER = 'flaskr/CleanText'
dirtyDictGlobal = {}

def create_filename(Gender, Location, Generation):
    gender = Gender[0].lower()
    location = Location[0].lower()
    generation = Generation[0].lower()

    currentName = location + gender + generation
    if os.path.exists('flaskr/DirtyAudio/'+currentName+".wav"):
        Number = 1
        while(os.path.exists('flaskr/DirtyAudio/'+currentName+str(Number)+".wav")):
            Number += 1;
        return currentName+str(Number)+".wav"
    else:
        return currentName+".wav"


def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = "secret key"
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def accept():
        for filename in glob.glob("flaskr/DirtyAudio/*.wav"):
            os.remove(filename)
        for filename in glob.glob("flaskr/DirtyText/*.txt"):
            os.remove(filename)
        return render_template('Accept.html')

    # Renders the template for upload
    @app.route('/Upload')
    def upload_form():
        return render_template('Upload.html')

    @app.route('/Upload', methods = ["POST"])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            location = request.form['Location']
            generation = request.form['Generation']
            gender = request.form['Gender']
            if file.filename == '':
                flash('No file selected for uploading')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                file.filename == "testing.txt"
                filename = secure_filename(file.filename)
                filenameConvention = create_filename(gender, location, generation)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filenameConvention))
                flash('File successfully uploaded')
                # writes Speech Recognition to DirtyAudio folder
                with open("flaskr/DirtyText/" + filenameConvention + ".txt", "w") as file:
                    file.write(speech_recognize("flaskr/DirtyAudio/" + filenameConvention))
                return redirect('/Upload')
            else:
                flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
                return redirect(request.url)

    @app.route('/DataVisualization')
    def DataVisualization():
        # instantiates K-Means with no stop-words
        instance = K_Means([])
        # returns rendered template
        return render_template('DataVisualization.html', global_representation_py = instance.representation, dirty_texts_py = instance.dirty_texts)

    @app.route("/UpdateDataVisualization/<data>", methods = ["GET", "POST"])
    def UpdateDataVisualization(data):
        # instantiates K-Means with user selected stop-words
        updated_instance = K_Means(data.split(","))
        # returns AJAX response
        return json.dumps({"representation": updated_instance.representation})

    if __name__ == "__main__":
        app.run()

    return app
