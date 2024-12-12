# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import io

# Модуль для визуализации
def show_plots(user_tasks):

    def get_month(date):
        months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                  'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
        month = int(date.split('-')[1])
        return months[month - 1]

    df = pd.DataFrame(user_tasks)

    df['deadline'] = pd.to_datetime(df['deadline'], dayfirst=True)
    df['month'] = df['deadline'].dt.to_period('M')
    df['day'] = df['deadline'].dt.day
    df['status_label'] = df['status'].apply(lambda x: 'Выполнено' if x == 1 else 'Не выполнено')

    yearly_summary = df.groupby(['month', 'status_label']).size().unstack(fill_value=0)

    current_month = datetime.now().strftime('%Y-%m')
    monthly_tasks = df[df['month'] == current_month]
    daily_summary = monthly_tasks.groupby(['day', 'status_label']).size().unstack(fill_value=0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    days_in_month = pd.Period(current_month).days_in_month
    daily_summary = daily_summary.reindex(range(1, days_in_month + 1), fill_value=0)

    daily_summary.plot(kind='bar', stacked=True, ax=ax1, color=['#4CAF50', '#FF4C4C'], alpha=0.7)
    ax1.set_title(f'Состояние задач за текущий месяц ({get_month(current_month)})')
    ax1.set_xlabel('Число')
    ax1.set_xticklabels(range(1, days_in_month + 1), rotation=45)
    ax1.set_ylabel('Количество задач')
    ax1.legend(title='Состояние')
    ax1.grid(axis='y')
    ax1.set_ylim(0, daily_summary.values.max() + 5)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

    yearly_summary.plot(kind='bar', stacked=True, ax=ax2, color=['#4CAF50', '#FF4C4C'], alpha=0.7)
    ax2.set_title('Состояние задач по месяцам')
    ax2.set_xlabel('Месяц')
    ax2.set_ylabel('Количество задач')
    ax2.legend(title='Состояние')
    ax2.grid(axis='y')
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format = 'png')
    buf.seek(0)
    return buf