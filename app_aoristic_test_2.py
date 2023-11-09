import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Function to execute workflow
def execute_workflow():
    # Set variable names
    comm_date_fr = comm_date_fr_name.get()
    comm_date_to = comm_date_to_name.get()
    comm_time_fr = comm_time_fr_name.get()
    comm_time_to = comm_time_to_name.get()

    # Read the uploaded CSV
    df = pd.read_csv(file_path.get())

    # Data cleaning and preprocessing
    df.fillna({comm_date_to: df[comm_date_fr], comm_time_to: df[comm_time_fr]}, inplace=True)
    df.dropna(subset=[comm_date_fr, comm_date_to, comm_time_fr, comm_time_to], inplace=True)
    df['start_date'] = pd.to_datetime(df[comm_date_fr].astype(str) + ' ' + df[comm_time_fr].astype(str), format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df['end_date'] = pd.to_datetime(df[comm_date_to].astype(str) + ' ' + df[comm_time_to].astype(str), format='%d/%m/%Y %H:%M:%S', errors='coerce')
    #df['start_date'] = df['start_date'].dt.strftime('%d/%m/%Y %H:%M:%S')
    #df['end_date'] = df['end_date'].dt.strftime('%d/%m/%Y %H:%M:%S')

    # Generate and save Seaborn plots
    output_directory_path = output_directory.get()
    if not os.path.exists(output_directory_path):
        os.makedirs(output_directory_path)

    # Aoristic analysis calculations by day
    daily_totals = np.zeros(7)
    for index, row in df.iterrows():
        start_day = row['start_date'].weekday()
        end_day = row['end_date'].weekday()

        # total days the event spans
        total_days = end_day - start_day + 1

        # events with identical start/end days
        if total_days == 0:
            total_days = 1

        # distribute value of 1 event over span
        value_per_day = 1 / total_days

        for day in range(start_day, end_day + 1):
            daily_totals[day] += value_per_day

    # Aoristic totals by day of the week bar plot
    plt.figure(figsize=(14, 6))
    # context
    sns.set_context("notebook")
    # daily totals to percentages
    daily_percentages = (daily_totals / daily_totals.sum()) * 100
    # weekday names for the x-axis
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # style
    sns.set_style("whitegrid")
    # bar plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=days, y=daily_percentages, color='#135DD8')
    # title and labels
    plt.title("Proportion of offences per day")
    plt.xlabel("Weekday")
    plt.ylabel("% of offences")
    plt.savefig(os.path.join(output_directory_path, 'aoristic_totals_by_day.png'))

    # Aoristic analysis calculations by hour
    hourly_totals = np.zeros(24)
    for index, row in df.iterrows():
        start_hour = row['start_date'].hour
        end_hour = row['end_date'].hour
        start_day = row['start_date'].weekday()
        end_day = row['end_date'].weekday()

        # total hours the event spans
        if start_day == end_day:
            total_hours = end_hour - start_hour + 1
        else:
            total_hours = (24 - start_hour) + end_hour + 1 + 24 * (end_day - start_day - 1)

        # events with identical start/end timestamps
        if total_hours == 0:
            total_hours = 1

        # distribute the value of 1 event over span
        value_per_hour = 1 / total_hours

        if start_day == end_day:
            for hour in range(start_hour, end_hour + 1):
                hourly_totals[hour] += value_per_hour
        else:
            for hour in range(start_hour, 24):
                hourly_totals[hour] += value_per_hour

            for day in range(start_day + 1, end_day):
                for hour in range(24):
                    hourly_totals[hour] += value_per_hour

            for hour in range(0, end_hour + 1):
                hourly_totals[hour] += value_per_hour

    # Aoristic totals by hour bar plot
    # context
    sns.set_context("notebook")
    # hourly totals to percentages
    hourly_percentages = (hourly_totals / hourly_totals.sum()) * 100
    # labels for the x-axis
    hours = list(range(24))
    # style
    sns.set_style("whitegrid")
    # bar plot
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x=hours, y=hourly_percentages, color='#135DD8')
    # title and labels
    plt.title("Proportion of offences per hour")
    plt.xlabel("Hour of the Day")
    plt.ylabel("% of offences")
    plt.savefig(os.path.join(output_directory_path, 'aoristic_totals_by_hour.png'))

    # Aoristic heatmap
    heatmap_totals = np.zeros((7, 24))
    for index, row in df.iterrows():
        start_day = row['start_date'].weekday()
        end_day = row['end_date'].weekday()
        start_hour = row['start_date'].hour
        end_hour = row['end_date'].hour

        # total hours the event spans
        if start_day == end_day:
            total_hours = end_hour - start_hour + 1
        else:
            total_hours = (24 - start_hour) + end_hour + 1 + 24 * (end_day - start_day - 1)

        # events with identical start/end timestamps
        if total_hours == 0:
            total_hours = 1

        # distribute the value of 1 event over span
        value_per_hour = 1 / total_hours

        if start_day == end_day:
            for hour in range(start_hour, end_hour + 1):
                heatmap_totals[start_day, hour] += value_per_hour
        else:
            for hour in range(start_hour, 24):
                heatmap_totals[start_day, hour] += value_per_hour

            for day in range(start_day + 1, end_day):
                for hour in range(24):
                    heatmap_totals[day, hour] += value_per_hour

            for hour in range(0, end_hour + 1):
                heatmap_totals[end_day, hour] += value_per_hour

    # heatmap plot
    # context
    sns.set_context("notebook")

    # heatmap totals to percentages
    heatmap_percentages = (heatmap_totals / np.sum(heatmap_totals)) * 100

    # weekday names y-axis
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # heatmap
    plt.figure(figsize=(14, 7))
    # with labels
    # ax = sns.heatmap(heatmap_percentages, cmap='flare', annot=True, fmt='.1f', linewidths=.5, cbar_kws={'label': '% of offences'}, annot_kws={'color': 'white', 'weight': 'bold'}, linecolor='white')
    # without labels
    ax = sns.heatmap(heatmap_percentages, cmap='vlag', annot=False, fmt='.1f', linewidths=.5, linecolor='white')

    # y-axis labels
    ax.set_yticklabels(days, rotation=0)

    # title
    plt.title("Proportion of offences by day and hour")
    plt.savefig(os.path.join(output_directory_path, 'aoristic_heatmap.png'))

    messagebox.showinfo('Info', f'Analysis completed. Files saved in {output_directory_path}')


# Create the main application window
root = tk.Tk()
root.title('Aoristic Analysis App')

# File selection widget
file_path = tk.StringVar()

def browse_file():
    file_path.set(filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')]))

tk.Label(root, text='Select CSV:').grid(row=0, column=0, sticky='w', padx=5, pady=5)
tk.Entry(root, textvariable=file_path, width=40).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text='Browse', command=browse_file).grid(row=0, column=2, padx=5, pady=5)

# Input column header names
# Commencing date from
comm_date_fr_name = tk.StringVar()

comm_date_fr_label = ttk.Label(root, text='Date from col name: ')
comm_date_fr_label.grid()
comm_date_fr_entry = ttk.Entry(root, width=15, textvariable=comm_date_fr_name)
comm_date_fr_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
comm_date_fr_entry.focus()

# Commencing date to
comm_date_to_name = tk.StringVar()

comm_date_to_label = ttk.Label(root, text='Date to col name: ')
comm_date_to_label.grid()
comm_date_to_entry = ttk.Entry(root, width=15, textvariable=comm_date_to_name)
comm_date_to_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
comm_date_to_entry.focus()

# Commencing time from
comm_time_fr_name = tk.StringVar()

comm_time_fr_label = ttk.Label(root, text='Time from col name: ')
comm_time_fr_label.grid()
comm_time_fr_entry = ttk.Entry(root, width=15, textvariable=comm_time_fr_name)
comm_time_fr_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
comm_time_fr_entry.focus()

# Commencing time to
comm_time_to_name = tk.StringVar()

comm_time_to_label = ttk.Label(root, text='Time to col name: ')
comm_time_to_label.grid()
comm_time_to_entry = ttk.Entry(root, width=15, textvariable=comm_time_to_name)
comm_time_to_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
comm_time_to_entry.focus()

# Output directory widget
output_directory = tk.StringVar()


def browse_directory():
    output_directory.set(filedialog.askdirectory())

tk.Label(root, text='Output Directory:').grid(row=6, column=0, sticky='w', padx=5, pady=5)
tk.Entry(root, textvariable=output_directory, width=40).grid(row=6, column=1, padx=5, pady=5)
tk.Button(root, text='Browse', command=browse_directory).grid(row=6, column=2, padx=5, pady=5)

# Execute button
tk.Button(root, text='Execute Workflow', command=execute_workflow).grid(row=7, column=0, columnspan=3, pady=10)

# Run the application
root.mainloop()