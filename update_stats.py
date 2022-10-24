from datetime import datetime,timedelta
import gspread
from numpy import record
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import calendar

def load_logs_from_gsheet() -> pd.DataFrame:

    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('./data/gsheetconfig.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('MoneyTracker').worksheet("logs")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    return df


def update_stats_sheets(last_day,today,weekly,monthly,year_sum_spended):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('./data/gsheetconfig.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('MoneyTracker').worksheet("TrackDashBoard")
    sheet.update('B13', last_day)
    sheet.update('B14', today)
    sheet.update('B15', weekly)
    sheet.update('B16', monthly)
    sheet.update('B19',year_sum_spended)

def calculate_summ(date_str:str,records:pd.DataFrame) -> float:
    summ = 0
    for index,row in records.iterrows():
        row_date = row.date_insert.split(' ')[0]
        date_str_split = date_str.split(' ')[0]
        if date_str_split == row_date:

            summ += float(row.summ)

    return summ


def calculate_summ_ranged(date_start: str,  date_end: str, records: pd.DataFrame) -> float:

    records['date_insert'] = pd.to_datetime(records['date_insert'], format='%m/%d/%Y %H:%M')
    mask = (records['date_insert'] >= date_start.split(' ')[0]) & (records['date_insert'] <= date_end.split(' ')[0])

    return records.loc[mask,"summ"].sum()


def main() -> None:
    today = datetime.now().date()
    today_str = today.strftime("%m/%d/%Y %H:%M")

    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime("%m/%d/%Y %H:%M")

    current_week_day = today.weekday()

    start_week = datetime.now() - timedelta(days=current_week_day)
    start_week_str = start_week.strftime("%m/%d/%Y %H:%M")

    end_week = start_week + timedelta(days=current_week_day)
    end_week = end_week + timedelta(hours=23)
    end_week = end_week + timedelta(minutes=59)

    end_week_str = end_week.strftime("%m/%d/%Y %H:%M")

    current_month = today.month
    current_year = today.year

    start_month_date,last_month_date = calendar.monthrange(current_year, current_month)
    month_start_date = datetime(current_year, current_month, 1)
    month_start_date_str = month_start_date.strftime("%m/%d/%Y %H:%M")

    month_end_date = datetime(current_year, current_month, last_month_date, 23, 59, 59)
    month_end_date_str = month_end_date.strftime("%m/%d/%Y %H:%M")


    current_year_date_start = datetime(current_year,1,1)
    current_year_date_start_str = current_year_date_start.strftime("%m/%d/%Y %H:%M")

    current_year_date_end = datetime(current_year,12, 31, 23, 59, 59)
    current_year_date_end_str = current_year_date_end.strftime("%m/%d/%Y %H:%M")

    print('Loading data')
    records = load_logs_from_gsheet()
    records = records[records.type != 'income']
    print('Calculating...')
    todays_summ_spended = calculate_summ(today_str,records)
    yesterdays_summ_spended = calculate_summ(yesterday_str,records)
    week_summ_spended = calculate_summ_ranged(start_week_str,end_week_str, records=records)
    month_sum_spended = calculate_summ_ranged(month_start_date_str,month_end_date_str,records)
    year_sum_spended = calculate_summ_ranged(current_year_date_start_str, current_year_date_end_str,records)

    print('Updating sheet..')
    update_stats_sheets(yesterdays_summ_spended, todays_summ_spended, week_summ_spended, month_sum_spended,year_sum_spended)
    print('Done')


if __name__ == "__main__":
    main()

