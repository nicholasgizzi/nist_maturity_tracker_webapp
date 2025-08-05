# Setup (local development)

1. Clone:

git clone https://github.com/nicholasgizzi/nist_tracker_webapp.git
cd nist_tracker_webapp

2. Setup virtual environment:
   
python3 -m venv venv
source venv/bin/activate

4. Install requirements:

pip install -r requirements.txt

6. Copy config template and customize:

cp instance/config.example.py instance/config.py

7. Initialize or upgrade the db:

flask db upgrade
python seed.py # this seeds the database with the NIST CSF framework functions, categories, and labels

8. run the app:

flask run
