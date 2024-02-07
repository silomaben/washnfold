@echo off

rem Change the directory to your Django project's folder
cd C:\Users\BenardSilomaMasikond\Documents\django\washnfold

rem Activate the virtual environment
call env\Scripts\activate

rem Run the Django development server
python manage.py runserver

rem Open the default browser to the Django app
start http://localhost:8000

rem Keep the command prompt window open
cmd /k
