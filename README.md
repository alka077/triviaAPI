# API Development and Documentation Final Project

## Trivia App

## Pre-requisites and Local Development
Developers using this project should already have Python3, pip and node installed on their local machines.

# Backend
From the backend folder run pip install requirements.txt. All required packages are included in the requirements file.

To run the application run the following commands:

    $env:FLASK_APP="flaskr"
    $env:FLASK_ENV="development"
    flask run

These commands put the application in development and directs our application to use the __init__.py file in our flaskr folder. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. If running locally on Windows, look for the commands in the Flask documentation.

The application is run on http://127.0.0.1:5000/ by default and is a proxy in the frontend configuration.

# Frontend
From the frontend folder, run the following commands to start the client:

    npm install // only once to install dependencies
    npm start 

By default, the frontend will run on localhost:3000.


