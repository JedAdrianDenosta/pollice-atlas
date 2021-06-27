# An Election System for WVSU CICT 

## Technologies Used

### Front-End
- HTML
- CSS
- Tailwind CSS Framework via npm package manager
- JavaScript
- NodeJS(code processors, styling, packages)

### Back-End
- Python
- Flask Framework
- MongoDB
- JavaScript

## Features

### Key Features
- [x] User Sign-up, Login, Logout
- [x] User Can Vote
- [x] User Can View Results in Real-time
- [x] User Can View News and Updates
- [x] User Can View About Page
- [x] User Can Edit their Profile Page
- [x] Admin Login, Logout
- [x] Admin Can Add Candidates
- [x] Admin Can Toggle ON/OFF the Voting
- [x] Admin Can Create a Post in News and Updates in Real-time
- [x] Admin Can Update Candidates
- [x] Admin Can Delete Candidates
- [x] Admin Can View Candidates
- [ ] Admin Can View Results Page in Real-time
- [ ] Admin Can View News and Updates Page in Real-time

### Other Features
- [x] Email Validation when user creates an account, only wvsu emails are allowed to create an account
- [x] Password Validation when user creates an account - password must contain at least 6 characters, one upper case letter and a number
- [x] Highest votes are colored
- [x] Users can only choose one candidate for every position and users Must choose a candidate for every position else they won't be able to submit their votes


### Future Updates
- [ ] Change Display Picture
- [ ] Let Admin create/edit/delete parties and choose party color
- [ ] Give access to Admin in the admin panel to see the users that have voted along with their credentials, specifically their email and/or name for vote validity purposes

## STEP 1: How to import Pollice-Temporary Database to MongoDB

1. Download and install MongoDB Community Server. You can download the Community Server here: https://www.mongodb.com/try/download/community?tck=docs_server
2. Add MongoDB's bin folder to PATH to be able to run the commands anywhere in your command line.
3. Download and extract MongoDB database tools to Mongo DB's bin folder. These tools will enable us to use the mongoimport command for us to be able to import our .json files into our MongoDB database. You can download the Tools here: https://www.mongodb.com/try/download/database-tools?tck=docs_databasetools
4. Create a new Connection in MongoDB and then create a Database. Important: Name the database 'election-system-test'. You can change this to whatever you want but you will need to make changes in the source code by editing this line db = client.get_database('election-system-test') and changing 'election-system-test' to match your database name. This code can be found in the routes.py and model.py for the mean time. We will update the init.py soon so you can change it in one place only.
5. Import our .json files from Pollice-Temporary-Database folder to our newly created database. Open your command line and we can do this by typing the command, mongoimport --db dbNameHere --collection collectionNameHere --file fileInputNameher.json usage example mongoimport --db election-system-test --collection admins --file admins.json. Do this for every .json file that we have.
6. And you're good to go!

## STEP 2: How to run (make sure you imported the necessary .json files in our database before proceeding)

1. Create a virtual environment in Python.
2. Activate python virtual environment with this command: source venvFolderName/bin/activate for linux users, kindly see documentation for windows users. Make sure you're on the right directory, specifically where your project folder is.
3. pip install -r requirements.txt to install flask packages
4. Install packages including: flask, bcrypt(for password hashing), pymongo(to make a connection, query and make changes in our MongoDB database)
5. npm install to install npm packages from package.json
6. npm run develop:css to build Tailwind for development (no purge) and start Flask application by running python run.py
7. When ready for production run npm run build:css to prepare a purged CSS build for production

