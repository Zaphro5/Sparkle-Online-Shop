GETTING STARTED

#Use the Command Prompt or Gitbash and not the VS Code Terminal
cd Sparkle_TeamAlola
python -m venv sparklevenv
source: sparklevenv/Scripts/activate
#Go back to Sparkle_TeamAlola directory and type: pip install -r requirements.txt
#Run the main.py

Note:
    I config two paths for database using sqlite or mysql-xampp. Just comment out the one you're not going to use. If you want to use mysql-xampp as database, create the database first in accordance 
    to the DB_NAME stated in the __init__.py. For this, I set the default to sqlite, but you can change to mysql-xampp if you want especially in actual production. To view the database, use the sqlite viewer on web and just open the database file there.