
# Django Game Store

This repository contains the project implemented for the Web Software Development course during my time as a student at Aalto University.

Project Plan
-----------------------

### 1. Team

- LK
- AG
- NP

### 2. General Description

We are planning to implement all features listed in the project description document.

### 3. Models

- Payment
    - user [User]
    - game [Game]
    - timestamp
    - price
    - ref
- Category
    - name
    - games [[Game]]
- Game
    - url
    - name
    - developer [User]
    - price
    - description
    - category [Category]
    - timestamp
    - sales [[Payment]]
    - highscores [[Highscores]]
    - state [GameState]
- Highscores
    - game [Game]
    - user [User]
    - score
    - timestamp
- GameState
    - user
    - game
    - state

### 4. Work

For collaboration and issue tracking, we use the functionality of GitLab. We scheduled weekly face-to-face meetings to discuss the current progress.

### 5. Schedule

|    Until   | Description                                              |
|:----------:|----------------------------------------------------------|
| 11.01.2019 | Models finished                                          |
| 18.01.2019 | Implemented Basic Functionality without Payment services |
| 25.01.2019 | Include payment services                                 |
| 01.02.2019 | Implement additional features                            |
| 08.02.2019 | Bug Hunting & Deployment                                 |
| 19.02.2019 | Finalizing the project                                   |


Features
-----------------------

### Authentication

### Basic player functionalities

### Basic developer functionalities

### Game/service interaction

### Save/load and resolution feature

### 3rd party login

### RESTful API

### Own game

### Social media sharing


Deployment
-----------------------

The project can be deployed to heroku using the heroku CLI. To install the heroku CLI follow the instructions on the official documentation (https://devcenter.heroku.com/articles/heroku-cli)

To deploy the code one need to create a new project using the following command or init the cloned project according to the documentation (https://devcenter.heroku.com/articles/git#for-an-existing-heroku-app)
```
heroku create
heroku config:set SECRET_KEY=[DJANGO SECRET KEY]
```

Afterwards the project of the master branch can be deployed with the following command:
```
git push heroku master
```

#### Test Deployment

The project is deployed with a test configuration at [https://floating-chamber-37378.herokuapp.com](https://floating-chamber-37378.herokuapp.com)

We added five users:

- admin 
- gamer1
- gamer2
- developer1
- developer2

The passwords for the test users equal to their user names. This is only the case for those specific users. Registering new users requires to comply with password policies.

Configuration 
-----------------------

#### Payment service

To use the payment service, one need to configure a seller id and the seller secret (http://payments.webcourse.niksula.hut.fi/key/)

```
heroku config:set SELLER_ID=[Selled ID] SELLER_SECRET=[Secret Key]
```

#### Create Superuser

To create a admin superuser for django, one can run the following command:

```
heroku run python manage.py createsuperuser
```

The superuser is needed to setup the third party login.

#### Third Party Login

We implemented third party login for the providers Google and GitHub. The configuration should be done according to https://django-allauth.readthedocs.io/en/latest/providers.html#google and https://django-allauth.readthedocs.io/en/latest/providers.html#github. For both services a new entry in the `social applications` has to be added with a valid client id and the matching secret key.
````
