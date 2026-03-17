import pandas as pd
import os
from pathlib import Path

# Load the Summary.csv file
summary_df = pd.read_csv(r'/Users/suhaas/Machine-Learning/manu-sus-engine/Summary.csv')

# Initialize lists to store average and max values
avg_humidity_list = []
avg_flow_rate_list = []
avg_vibration_list = []
max_vibration_list = []

# Get the directory where batch files are located
batch_dir = Path('.')

# Process each batch
for idx, row in summary_df.iterrows():
    batch_id = row['Batch_ID']
    batch_file = batch_dir / f'Batch_{batch_id}.csv'
    
    if batch_file.exists():
        try:
            batch_df = pd.read_csv(batch_file)
            
            # Calculate average humidity
            if 'Humidity_Percent' in batch_df.columns:
                avg_humidity = batch_df['Humidity_Percent'].mean()
                avg_humidity_list.append(avg_humidity)
            else:
                avg_humidity_list.append(None)
            
            # Calculate average flow rate
            if 'Flow_Rate_LPM' in batch_df.columns:
                avg_flow_rate = batch_df['Flow_Rate_LPM'].mean()
                avg_flow_rate_list.append(avg_flow_rate)
            else:
                avg_flow_rate_list.append(None)
            
            # Calculate average vibration
            if 'Vibration_mm_s' in batch_df.columns:
                avg_vibration = batch_df['Vibration_mm_s'].mean()
                max_vibration = batch_df['Vibration_mm_s'].max()
                avg_vibration_list.append(avg_vibration)
                max_vibration_list.append(max_vibration)
            else:
                avg_vibration_list.append(None)
                max_vibration_list.append(None)
            
            print(f"Batch {batch_id}: Humidity={avg_humidity_list[-1]:.2f}%, Flow Rate={avg_flow_rate_list[-1]:.2f} LPM, Avg Vibration={avg_vibration_list[-1]:.4f} mm/s, Max Vibration={max_vibration_list[-1]:.4f} mm/s")
        except Exception as e:
            print(f"Error processing Batch_{batch_id}.csv: {e}")
            avg_humidity_list.append(None)
            avg_flow_rate_list.append(None)
            avg_vibration_list.append(None)
            max_vibration_list.append(None)
    else:
        print(f"Warning: Batch_{batch_id}.csv not found")
        avg_humidity_list.append(None)
        avg_flow_rate_list.append(None)
        avg_vibration_list.append(None)
        max_vibration_list.append(None)

# Add the new columns to the summary dataframe
summary_df['Avg_Humidity_Percent'] = avg_humidity_list
summary_df['Avg_Flow_Rate_LPM'] = avg_flow_rate_list
summary_df['Avg_Vibration_mm_s'] = avg_vibration_list
summary_df['Max_Vibration_mm_s'] = max_vibration_list
summary_df = summary_df.drop(columns=['Phases'])  # Remove the Phases column if it exists

# Save the updated Summary.csv
summary_df.to_csv('Summary.csv', index=False)
print("\nSummary.csv has been updated with new columns!")
print(f"Updated Summary.csv shape: {summary_df.shape}")
print("\nFirst few rows with new columns:")
print(summary_df[['Batch_ID', 'Avg_Humidity_Percent', 'Avg_Flow_Rate_LPM', 'Avg_Vibration_mm_s', 'Max_Vibration_mm_s']].head(10))
