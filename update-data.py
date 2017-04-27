import csv
from glob import glob
from random import randint, shuffle
import shutil

user_ids = [
  3069,
3021,
3030,
3060,
3075,
3022,
3077,
3045,
3032,
3061,
3054,
3033,
3065,
3052,
3064,
3057,
3036,
3079,
3012,
3047,
3038
]
for fn in glob('data/consumption/*.csv'):
  user_id = fn.replace('data/consumption/', '').replace('.csv', '')
  if int(user_id) in user_ids:
    shutil.move(fn, 'data/%s.csv' % user_id)

#   user_id = fn.replace('data/consumption/', '').replace('.csv', '')
#   user_ids.append(user_id)

# shuffle(user_ids)
# area_tariffs = {
#   'a1': ['t1', 't2'],
#   'a2': ['t3'],
# }

# with open('data/user_data.csv', 'w') as f:
#   writer = csv.writer(f)
#   writer.writerow(['id', 'area', 'tariff'])
#   for user_id in user_ids:
#     area = area_tariffs.keys()[randint(0,1)]
#     tariff = area_tariffs[area][randint(0,len(area_tariffs[area])-1)]
#     writer.writerow([user_id, area, tariff])


