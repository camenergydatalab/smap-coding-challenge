# The Report of the full stack challenge

## Usage(local)

```
pip install -r requirements.txt
cd dashboard
python manage.py makemigrations
python manage.py migrate
python manage.py import
python manage.py runserver
```

## Technical Decision

Time-series data of consumption is too big. Because I fear database bloat, I adopt csv files. So, Time-series data is not treated as Model, but there is no necessary to think about scaling database. Some often-used data(e.g. total/average consumption per user) is stored in database.

## Future

- improve design(chart, alignment, color, font-size, etc...)
- think how to visualize data of consumption
- think how to add data
  - make batch script to combine csv files
  - use NoSQL database such as AWS DynamoDB
- make unittest
