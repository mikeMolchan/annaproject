import datetime as dt


str = '2025-07-19'
converted_date = dt.datetime.strptime(str, "%Y-%m-%d").date()
print((converted_date - dt.datetime.now().date()).days)