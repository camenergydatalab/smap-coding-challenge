SMAP Python Developer Challenge
====

### Why do we ask you to do this challenge?

As part of the SMAP interview process, we are asking you to work on a small coding exercise to help us understand your skills, and give you an idea of the work you would be doing with us.

We estimate that this can be done in less than half a day but there is no time limit.

### The challenge

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

* Python 3.6 or later
* Django 1.11

To work on the challenge, please fork this repository or download it. After you have finished, you can send us a link to the fork or simply zip the repository and email it to us.

### Questions?

Please ask us! If something doesn't work or you have a question about the data, get in touch and we will help.

### What happens after the challenge?

We will review it and then get back to you as soon as possible. We appreciate the time it takes to do this and we will provide feedback.

#### How we review

**We value code quality more than the number of features**. If anything has been left out, please leave a comment in `REPORT.md` so that we know.

We will assess the following aspects:

* **Architecture**: How did you process and store the data? How is the separation between frontend and backend?
* **Correctness**: Does the application do what was asked? If there is anything missing, was it documented and explained? (in `REPORT.md`)
* **Code quality**: Is the code easy to understand? Is it maintainable? Could we deploy it in production?
* **Testing**: How thorough are the tests?
  * Full coverage is not essential, we just want to get an idea of your testing skills
