import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV data into a pandas DataFrame
data = pd.read_csv('exercise_data.csv', names=['timestamp', 'angle_shoulder_elbow_wrist', 'angle_hip_shoulder_elbow', 'state', 'si_no'])

# Convert timestamp to datetime
data['timestamp'] = pd.to_datetime(data['timestamp'], format='%H:%M:%S')

# 1. Angle Plots over Time
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(data['timestamp'], data['angle_shoulder_elbow_wrist'])
plt.xlabel('Time')
plt.ylabel('Angle (shoulder-elbow-wrist)')
plt.title('Angle over Time')

plt.subplot(2, 1, 2)
plt.plot(data['timestamp'], data['angle_hip_shoulder_elbow'])
plt.xlabel('Time')
plt.ylabel('Angle (hip-shoulder-elbow)')
plt.title('Angle over Time')
plt.tight_layout()
plt.show()

# 2. State Transition Visualization
states = data['state'].unique()
for state in states:
    data.loc[data['state'] == state, 'state'] = state.capitalize()

state_counts = data.groupby('state').size()
state_counts.plot(kind='bar')
plt.xlabel('State')
plt.ylabel('Count')
plt.title('State Transition Visualization')
plt.show()

# 3. Repetition Analysis
repetitions = data.groupby('si_no').size()
repetitions.plot(kind='line')
plt.xlabel('Repetition Number')
plt.ylabel('Count')
plt.title('Repetition Analysis')
plt.show()

# 4. Angle Distribution Plot
plt.figure(figsize=(8, 6))
sns.kdeplot(data['angle_shoulder_elbow_wrist'], shade=True, label='Shoulder-Elbow-Wrist')
sns.kdeplot(data['angle_hip_shoulder_elbow'], shade=True, label='Hip-Shoulder-Elbow')
plt.xlabel('Angle')
plt.ylabel('Density')
plt.title('Angle Distribution')
plt.legend()
plt.show()

# 5. Angle Correlation Plot
plt.figure(figsize=(6, 6))
plt.scatter(data['angle_shoulder_elbow_wrist'], data['angle_hip_shoulder_elbow'])
plt.xlabel('Angle (shoulder-elbow-wrist)')
plt.ylabel('Angle (hip-shoulder-elbow)')
plt.title('Angle Correlation')
plt.show()

# 6. Angle Box Plots
plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
sns.boxplot(data=data, x='state', y='angle_shoulder_elbow_wrist')
plt.xlabel('State')
plt.ylabel('Angle (shoulder-elbow-wrist)')
plt.title('Angle Distribution by State')

plt.subplot(1, 2, 2)
sns.boxplot(data=data, x='state', y='angle_hip_shoulder_elbow')
plt.xlabel('State')
plt.ylabel('Angle (hip-shoulder-elbow)')
plt.title('Angle Distribution by State')
plt.tight_layout()
plt.show()

# 7. Angle Violin Plots
plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
sns.violinplot(data=data, x='state', y='angle_shoulder_elbow_wrist')
plt.xlabel('State')
plt.ylabel('Angle (shoulder-elbow-wrist)')
plt.title('Angle Distribution by State')

plt.subplot(1, 2, 2)
sns.violinplot(data=data, x='state', y='angle_hip_shoulder_elbow')
plt.xlabel('State')
plt.ylabel('Angle (hip-shoulder-elbow)')
plt.title('Angle Distribution by State')
plt.tight_layout()
plt.show()

# 8. Angle Histograms
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.hist(data['angle_shoulder_elbow_wrist'], bins=20, edgecolor='black')
plt.xlabel('Angle (shoulder-elbow-wrist)')
plt.ylabel('Frequency')
plt.title('Angle Histogram')

plt.subplot(1, 2, 2)
plt.hist(data['angle_hip_shoulder_elbow'], bins=20, edgecolor='black')
plt.xlabel('Angle (hip-shoulder-elbow)')
plt.ylabel('Frequency')
plt.title('Angle Histogram')
plt.tight_layout()
plt.show()

# 9. Angle Heatmap
plt.figure(figsize=(8, 6))
angle_corr = data[['angle_shoulder_elbow_wrist', 'angle_hip_shoulder_elbow']].corr()
sns.heatmap(angle_corr, annot=True, cmap='coolwarm')
plt.title('Angle Correlation Heatmap')
plt.show()

# 10. Time Series Analysis
'''time_series = data.set_index('timestamp').resample('1S').mean()
time_series = time_series.interpolate(method='linear')  # Interpolate missing values

plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
time_series['angle_shoulder_elbow_wrist'].plot()
plt.xlabel('Time')
plt.ylabel('Angle (shoulder-elbow-wrist)')
plt.title('Time Series Analysis')

plt.subplot(2, 1, 2)
time_series['angle_hip_shoulder_elbow'].plot()
plt.xlabel('Time')
plt.ylabel('Angle (hip-shoulder-elbow)')
plt.title('Time Series Analysis')
plt.tight_layout()
plt.show()

# 11. Progress Tracking (Correct Reps)
correct_reps = data[data['state'] == 'bottom'].groupby([pd.Grouper(key='timestamp', freq='D')])['si_no'].count()
correct_reps.plot(kind='line')
plt.xlabel('Date')
plt.ylabel('Correct Reps')
plt.title('Progress Tracking (Correct Reps)')
plt.show()

# 12. Progress Tracking (Incorrect Reps)
incorrect_reps = data[data['state'] != 'bottom'].groupby([pd.Grouper(key='timestamp', freq='D')])['si_no'].count()
incorrect_reps.plot(kind='line')
plt.xlabel('Date')
plt.ylabel('Incorrect Reps')
plt.title('Progress Tracking (Incorrect Reps)')
plt.show()

# 13. Progress Tracking (Total Reps)
total_reps = data.groupby([pd.Grouper(key='timestamp', freq='D')])['si_no'].count()
total_reps.plot(kind='line')
plt.xlabel('Date')
plt.ylabel('Total Reps')
plt.title('Progress Tracking (Total Reps)')
plt.show()# 11. Progress Tracking (Correct Reps)
correct_reps = data[data['state'] == 'bottom'].groupby([pd.Grouper(key='timestamp', freq='D')])['si_no'].count()
correct_reps.plot(kind='line')
plt.xlabel('Date')
plt.ylabel('Correct Reps')
plt.title('Progress Tracking (Correct Reps)')
plt.show()

# 12. Progress Tracking (Incorrect Reps)
incorrect_reps = data[data['state'] != 'bottom'].groupby([pd.Grouper(key='timestamp', freq='D')])['si_no'].count()
incorrect_reps.plot(kind='line')
plt.xlabel('Date')
plt.ylabel('Incorrect Reps')
plt.title('Progress Tracking (Incorrect Reps)')
plt.show()

# 13. Progress Tracking (Total Reps)
total_reps = data.groupby([pd.Grouper(key='timestamp', freq='D')])['si_no'].count()
total_reps.plot(kind='line')
plt.xlabel('Date')
plt.ylabel('Total Reps')
plt.title('Progress Tracking (Total Reps)')
plt.show()'''