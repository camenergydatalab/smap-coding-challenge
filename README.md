SMAP Python Developer Challenge
====

### Why do we ask you to do this challenge?

As part of the SMAP interview process, we are asking you to work on a small coding exercise to help us understand your skills, and give you an idea of the work you would be doing with us.

We estimate that this can be done in less than half a day but there is no time limit.

## Challenge 1 - The Full Stack Challenge

#### Background

We have a small dataset of users (in `data/user_data.csv`) and their electricity smart meters (in `data/consumption/<user_id>.csv`).  We want to help an energy provider view and analyse this data. One of the ways we do this is to visualise aggregated data (e.g. total consumption or average consumption) in a chart. We also want to show a list of users in a table.

#### Objectives

We have created a basic Django site, the challenge is for you to implement a small analysis application with the following features:

* Components to read and store user data and consumption data
  * Implement the command in `dashboard/consumption/management/commands/import.py`
  * This can be executed by running `python manage.py import` in the terminal
* Implementation of an aggregation for consumption data (e.g. total/average)
* Complete the `summary` view in `dashboard/consumption/views.py` and frontend code in `dashboard/consumption/templates/consumption/summary.html`
  * This page should contain at least one chart and one table
  * For instance a line chart showing the total consumption (aggregation of all users) and a table listing all users.
* (optional) Implement the `detail` view
  * This page should contain data for an individual consumer
  * For instance a line chart showing the consumption of an individual consumer, and a list of fields such as tariff, area, etc ...

The site (`dashboard`) includes one app (`consumption`). This is where you will implement your solution (you may also add additional apps if required). The Django app is configured with a sqlite DB for you to use.

Please document any technical decisions, trade-offs, problems etc. in `REPORT.md` in English.

If you have added any python packages, please add them to `requirements.txt`

### The data

* `data/user_data.csv`
  * A file containing user data

id | area | tariff
---|------|-------
1 | a1 | t1
2 | a1 | t2
3 | a2 | t3
... | ... | ...

* `data/consumption/<user_id>.csv`
  * A file containing energy consumption (in Wh) in 30 minute intervals

datetime | consumption
---------|------------
2016-07-01 00:00:00 | 100.
2016-07-01 00:30:00 | 130.
2016-07-01 01:00:00 | 90.
... | ...

### Development environment

* Python 3.7.x
* Django 2.2.x

To work on the challenge, please fork this repository or download it. After you have finished, you can send us a link to the fork or simply zip the repository and email it to us.


## Challenge 2 - The Frontend Challenge
#### Setup
The frontend challenge is located in the project folder `frontend`. To be able to use APIs you have to setup the dev environment:
* Create the dev python3 environment with `virtualenv -p python3 venv`.
* Activate environment: `source venv/bin/activate`.
* Install requirements: `pip install -r requirements.txt`.

After setup, please move to frontend folder (`cd frontend`) and run web server with `python manage.py runserver`. 

If you visit the browser at `http://localhost:8000` you will have to see a page with title **Frontend challenge.**

For the purpose of challenge, we prepared several apis you should use:
* `api/consumers` will return the list of all consumers;
* `api/consumers/<low|high|extra_high>` will return consumers of certain type (low voltage, high voltage, extra high voltage);
* `api/consumer/<consumer_id>` will return a particular consumer (GET) or delete (DELETE) a consumer;
* a POST request with params `name` and `consumer_type` to  `api/consumer` will create a new consumer;
* `api/monthly_statistics/<consumer_id>` will return a monthly statistics of a particular consumer with consumption, total_bill and total_cost data points. If you specify year param as: `api/monthly_statistics/<consumer_id>?year=2017` the api returns filtered results by year. The data contains 2016 and 2017. 

#### Objectives
The basic template files are in `frontend/app/templates/`. There is a `base.html` file which serves as a base template and `index.html` file, which is served as an index file. You can put static files in `frontend/app/static` folder. 
We prepared two static files for you:
* `frontend/app/static/css/style.css` for custom css and
* `frontend/app/statics/js/app.js` for custom js.
This files are already included in `base.html**. You can use them or include other files. If you free to use any other frontend technology and document it in REPORT.

**TASKS**
* Include CSS framework or create your own stylesheet. We would love to see some unique design touches.
* Create a reusable Vue component for displaying a list of consumers and filtering by consumer types. There should be options of deleting and adding consumers.
* Create a reusable Vue component for displaying a particular consumer, which includes a chart of Monthly Statistics data (consumption, total bill, total cost and calculated profit per month). This component should also implement filtering of the consumer data by year. There should be also total profit for a particular year or both years together (based on selection).
*  We are happy to see JS bundlers such as webpack or browserify, single file Vue components and CSS pre-processing.
* The site should be cross browser compatible and mobile ready. You can use any css framework you want.
* BONUS: frontend tests.



## Questions?

Please ask us! If something doesn't work or you have a question about the data, get in touch and we will help.

### What happens after the challenge?

We will review it and then get back to you as soon as possible. We appreciate the time it takes to do this and we will provide feedback.

#### How we review

**We value code quality more than the number of features**. Please document which browser(s) you used to check your work, as well as any technical decisions, trade-offs, problems etc. in `REPORT.md` in English. If anything has been left out, please also leave a comment in `REPORT.md` so that we know.

We will assess the following aspects:

* **Architecture**: How did you process and store the data? How is the separation between frontend and backend?
* **Correctness**: Does the application do what was asked? If there is anything missing, was it documented and explained? (in `REPORT.md`)
* **Code quality**: Is the code easy to understand? Is it maintainable? Could we deploy it in production?
* **Testing**: How thorough are the tests?
  * Full coverage is not essential, we just want to get an idea of your testing skills
