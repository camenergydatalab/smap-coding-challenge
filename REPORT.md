# Challenge Report

## Development Environment
- OS: Mac OS Mojave 10.14.6
- CPU: 2.2GHz Intel Core i7
- Memory: 16GB
- Browser: Google Chrome 88.0.4324.192

## Comment Style
Based on [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## Summary of added and changed files and directories

```
smap-coding-challenge
├── REPORT.md ... changed
├── dashboard
│   ├── consumption
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── management
│   │   │   └── commands
│   │   │       └── import.py ... changed
│   │   ├── migrations
│   │   │   └── 0001_initial.py ... changed
│   │   ├── models.py ... changed
│   │   ├── queries.py ... added for handle database object
│   │   ├── services.py ... added for handle service's logic
│   │   ├── templates
│   │   │   ├── 404.html ... added for returning custom 404 page
│   │   │   └── consumption
│   │   │       ├── common ... added for common js function and wrapping library
│   │   │       │   ├── chart-creator.html
│   │   │       │   └── table-creator.html
│   │   │       ├── detail.html ... changed
│   │   │       ├── layout.html ... changed
│   │   │       └── summary.html ... changed
│   │   ├── urls.py ... changed
│   │   └── views.py ... changed
│   ├── manage.py
│   ├── test_report ... added for saving test
│   │   └── coverage
│   └── tests ... added (for the detail, see "About Testing")
├── data
│   ├── consumption
│   ├── user_data.csv
│   └── validation_results ... added for saving validation's results
├── requirements.txt ... changed for installing additional libraries
└── requirements_dev.txt ... added for installing additional libraries in development environment
```

## 1. About import.py

### Technical descisions

#### Used library
- [pandas](https://pandas.pydata.org/)
  - For finding and handling duplication in csv file easily

#### How to install libraries

Execute commands below.
```
cd smap-coding-challenge
pip install -U -r requirements.txt
```

#### How to Execute command
Execute a command below.
```
python manage.py import --validation {option} --mode {option}
# e.g.
python manage.py import --validation no --mode first
```

Abput command usage, please see "Command Parameter" below, or execute command `python manage.py import --help` .

#### Command Parameter
- --validation: Validation before importing
  - yes: Execute validation before importing (default)
    - If duplicated data found, the indexes of those data will be recorded in `data/validation_results/{datetime}` folder for each file
  - no: Do not execute validation
- --mode
  - skip: Skip duplicated data
  - first: Select first one
  - last: Select last one
  - sum: Sum duplicated data if type is Number

#### Process of Importing CSV Data into Database

Below is about how the import.py store user data and consumption data in database.

##### 1. Validation
- Execute validation for each csv file
- If invalid data is founded, importing will be terminated and database will execute rollback
  - This time, only duplication checking is executed
- If specify `--validation no` in command, validation will not be executed
  - Therefore, to execute importing this challenge's data, please specify above parameter

##### 2. Importing User data
- Data in `user_data.csv` will be loaded and stored in database
  - Each file's log will be printed in the terminal
- If exception happened, importing will be terminated and database will execute rollback
- About Django models specification for user data
  - Model name in Django is `User`
  - `id` is stored as `Integer` and used as primary key
  - `area` is stored as `Character` and its max length is 2
  - `tariff` is stored as `Character` and its max length is 2

##### 3. Importing Consumption data
- Data in csv file in `consumption` folder will be loaded and stored in database (file-by-fle)
  - Each file log will be printed in the terminal
- If exception happened, importing will be terminated and database will execute rollback
- About Django models specification for consumption data
  - Model name in Django is `Consumption`
  - Integer `id` is created for primary key
  - `user_id` is stored as `ForeignKey` links to `User` model
  - `datetime` is converted to datetime object and stored as `DateTime`
  - `consumption` is stored as 10-digit `Decimal` in max and has one decimal place

### Trade-offs

#### Importing consumption data is executed file-by-file

I found that following pros and cons for file-by-file importing.

- Pros
  - Can avoid memory leak (the number of csv files is not known)
  - Can validate each csv data by pandas library
  - Can avoid exceedin Maximum SQL query size ([limited to 1,000,000 bites](https://www.sqlite.org/limits.html))

- Cons
  - The speed is slower than reading csv files in chunk which is not exceeding memory size and importing each data into database

### Problems

#### 1. import.py only check duplication
The import.py's validation function only check duplication so far. So if data in files is incorrect in other cases, unexpected error might occurs.
I suggest that if you want import data safely, add some another validation function to `import.py`.

#### 2. Max Consumption data's digit is limited to 10
Database can only hold max 10-digit decimal number. So if consumption data's value exceed 10-digit, importing data will be failed.
if you handle bigger data, I suggest that expand the max digits size of `consumption`.

### Testing
This case, I created test for each command parameter (not function-by-function). Because it is important to make sure that each command's result is right, and also each function in Command class is changeable.
About how to executing unit tests and structures of test files, please see "About Testing".

## 2. About summary view and detail view

### Browser Support
You can see both summary and detail views in the browsers below.
- Google Chrome
- Firefox
- Internet Explorer 11
- Microsoft Edge

### Technical descisions

#### Used Franeworks in Javascript

All below Frameworks are installed via cdn (in template/layout.html).

- [Polyfill.io](https://polyfill.io/)
  - For using ES6 Javascript functions and Coding Style
- [Moment.js](https://momentjs.com/)
  - For handling date and time objects in Javascript
- [Chart.js](https://www.chartjs.org/)
  - For showing consumption data in Chart
- [Tabulator](http://tabulator.info/)
  - For showing, sorting, visualizing user data in Table

#### Specification

##### Chart part in Summary View
Chart part shows two charts below.
- Total consumption every 30 minutes
  - A chart shows user's total consumption every 30 minutes
- Average consumption every 30 minutes
  - A chart shows user's average consumption every 30 minutes

And above each chart, there is a time period controller which has functions below.

- The select box on the left shows a time starts from
  - The options are elements every one day (time is 00:00:00)
- The select box on the right shows a time end to
  - The options are elements every one day (time is 00:00:00)
- Pushing Apply button do the setting of time period to the chart

##### Table part in Summary View
The table shows following info.
- ID: user's id
  - Filtering is available on the top of the culumn
- Area: user's area
  - Filtering is available on the top of the culumn
- Tariff: user's tariff
  - Filtering is available on the top of the culumn
- Average: user's average consumption in all period
  - Filtering by minimum value and maximum value is available on the top of the culumn
- Percentage of consumption to top user's average consumption: user's average consumption percentage to top user's average consumption
  - Filtering by minimum value and maximum value is available on the top of the culumn
  - If click a cell, use's detail view page will be opend

##### Chart part in Detail View
Chart part shows one chart below.
- A user's consumption every 30 minutes
  - function of time period controller is same as summary view

##### Table part in Detail View
The table shows following info.
- id: user's id
- area: user's area
- tariff: user's tariff

### Trade-offs

#### Using Framework for Charts and Tables

- Pros
  - Can show chart and table easily
  - Both Frameworks have wide broser support

- Cons
  - Cannot test the looking of chart and table
    - I tried [ImageMagick's compare function](https://imagemagick.org/script/compare.php) for comparing sample chart to chart created with selenium, but the result was inaccurate
      - Also I tried [needle](https://github.com/python-needle/needle), but the framework has less info and old

### Problems

#### No Error Logging
So far, there is no error logging. If you use app in production level, you should decide error log specification and write code.

#### Data Filtering is executed by frontend Javascript

- Pros
  - Can Avoid a lot of access to database
    - Speedy and stable if PC and browser are high spec

- Cons
  - Heavy to handle in Javascript if many data is loaded
    - It's better to create filtering function if you handle many data

### Testing
I created test for each function's unit test and integration test using browser maipulation.
About how to executing unit tests and integration tests, and structures of test files, please see "About Testing".

## 3. About Testing

### Technical descisions

#### Delete default tests.py and create `tests` folder
Because many tests should be written and it is easy to maintenance them, I deleted `tests.py`, then created `tests` directory in `dashboard` directory. And I created tests for each target file (e.g. import.py) in that directory. The directory structure is below (excluding `__init__.py` and python cache files).

```
tests
├── .coveragerc ... coverage setting for unittest
├── test_fixtures.py ... fixture data for testing
├── integtest
│   ├── driver
│   │   └── mac
│   │       └── chromedriver ... chrome driver for Mac OS
│   ├── test_detail.py ... tests for detail view page
│   └── test_summary.py ... tests for summary view page
└── unittest ... unit test directory
    └── consumption
    │   ├── management
    │   │   └── commands
    │   │       └── test_import.py ... tests for import.py
    │   ├── test_views.py ... tests for views.py
    │   └── test_services.py ... tests for services.py
    └── test_data
        ├── duplicated ... duplicated data for test
        │   ├── consumption
        │   │   ├── 1111.csv
        │   │   ├── 2222.csv
        │   │   └── 3333.csv
        │   └── user_data.csv
        ├── non_duplicated ... non duplicated data for test
        │   ├── consumption
        │   │   ├── 1111.csv
        │   │   ├── 2222.csv
        │   │   └── 3333.csv
        │   └── user_data.csv
        └── validation_results ... validation results folder for test
```

##### Libraries and a Driver for Testing
- [Coverage.py](https://pypi.org/project/coverage/)
  - For measuring code coverage
- [Selenium](https://pypi.org/project/selenium/)
  - For using browser in integration test
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/home)
  - For using selenium with chrome

##### How to install libraries
Execute commands below.
```
cd smap-coding-challenge
pip install -U -r requirements_dev.txt
```
The reason I separate the requirements_dev.txt from requirements.txt is that those library are only used for development purpose.

##### Preapareing ChromeDriver (NOTICE: Only confirmed on Mac OS environment)
To download driver, access the web site on "Libraries and a Driver for Testing" above, and choose the executable driver on your OS.
To execute test with driver, make sure below settings.

- Django has permissions to execute the driver. (e.g. `chmod 755 tests/integtest/driver/mac/chromedriver`)
- Define driver path in the `get_driver_path()` function in `tests/test_fixtures/`

### Unit test

#### Executing unit test and Creating coverage data
Execute a command below.
```
coverage run --rcfile=tests/.coveragerc manage.py test tests.unittest
```
Coverage module is executed with running tests and `.coverage` file will be created on current directory.

##### Generating html style report
Execute a command below.
```
coverage html -d test_report/coverage
```
After executing the command, html files will be generated in `test_report/coverage` folder.
To see the result, open the `index.html` in the folder with your browser.

### Integration test

#### Executing integration test
After the setting of "Preapareing ChromeDriver", execute command below.
```
python manage.py test tests.integtest
```

### Trade-offs

#### Manually define test data in test_fixtures.py

- Pros
  - Easy to reuse variable
  - Easy to create complicated data structures (e.g. datetime object)
  - Easy to calculate for each test data (e.g. calculate average consumption)

- Cons
  - If needs a lot of test data, it is little hard to maintain them
    - it is better to use the [fixture](https://docs.djangoproject.com/en/2.2/howto/initial-data/) or [factory-boy](https://github.com/FactoryBoy/factory_boy) in that case
