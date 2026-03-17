import pandas as pd
from pathlib import Path

# Load the Summary.csv file
summary_df = pd.read_csv(r'/Users/suhaas/Machine-Learning/manu-sus-engine/Summary.csv')

# Initialize lists to store average and max values
avg_humidity_list = []
max_humidity_list = []
avg_flow_rate_list = []
max_flow_rate_list = []
avg_motor_speed_list = []
avg_compression_force_list = []
max_power_consumption_list = []
max_pressure_list = []
avg_vibration_list = []
max_vibration_list = []

# Get the directory where batch files are located
batch_dir = Path(r'/Users/suhaas/Machine-Learning/manu-sus-engine/batchdata')

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
                max_humidity = batch_df['Humidity_Percent'].max()
                avg_humidity_list.append(avg_humidity)
                max_humidity_list.append(max_humidity)
                # Replace 0 values with mean
                humidity_mean = batch_df['Humidity_Percent'][batch_df['Humidity_Percent'] > 0].mean()
                batch_df.loc[batch_df['Humidity_Percent'] == 0, 'Humidity_Percent'] = humidity_mean
            else:
                avg_humidity_list.append(None)
                max_humidity_list.append(None)
            
            # Calculate average flow rate (only values > 0)
            if 'Flow_Rate_LPM' in batch_df.columns:
                flow_data = batch_df['Flow_Rate_LPM']
                avg_flow_rate = flow_data[flow_data > 0].mean()
                max_flow_rate = batch_df['Flow_Rate_LPM'].max()
                avg_flow_rate_list.append(avg_flow_rate)
                max_flow_rate_list.append(max_flow_rate)
                # Replace 0 values with mean
                batch_df.loc[batch_df['Flow_Rate_LPM'] == 0, 'Flow_Rate_LPM'] = avg_flow_rate
            else:
                avg_flow_rate_list.append(None)
                max_flow_rate_list.append(None)
            
            # Calculate average motor speed (only values > 0)
            if 'Motor_Speed_RPM' in batch_df.columns:
                motor_data = batch_df['Motor_Speed_RPM']
                avg_motor_speed = motor_data[motor_data > 0].mean()
                avg_motor_speed_list.append(avg_motor_speed)
                # Replace 0 values with mean
                batch_df.loc[batch_df['Motor_Speed_RPM'] == 0, 'Motor_Speed_RPM'] = avg_motor_speed
            else:
                avg_motor_speed_list.append(None)
            
            # Calculate average compression force (only values > 0)
            if 'Compression_Force_kN' in batch_df.columns:
                compression_data = batch_df['Compression_Force_kN']
                avg_compression_force = compression_data[compression_data > 0].mean()
                avg_compression_force_list.append(avg_compression_force)
                # Replace 0 values with mean
                batch_df.loc[batch_df['Compression_Force_kN'] == 0, 'Compression_Force_kN'] = avg_compression_force
            else:
                avg_compression_force_list.append(None)
            
            # Calculate max power consumption
            if 'Power_Consumption_kW' in batch_df.columns:
                max_power = batch_df['Power_Consumption_kW'].max()
                max_power_consumption_list.append(max_power)
            else:
                max_power_consumption_list.append(None)
            
            # Calculate max pressure
            if 'Pressure_Bar' in batch_df.columns:
                max_pressure = batch_df['Pressure_Bar'].max()
                max_pressure_list.append(max_pressure)
            else:
                max_pressure_list.append(None)
            
            # Calculate average vibration
            if 'Vibration_mm_s' in batch_df.columns:
                avg_vibration = batch_df['Vibration_mm_s'].mean()
                max_vibration = batch_df['Vibration_mm_s'].max()
                avg_vibration_list.append(avg_vibration)
                max_vibration_list.append(max_vibration)
            else:
                avg_vibration_list.append(None)
                max_vibration_list.append(None)
            
            # Save the modified batch file back
            batch_df.to_csv(batch_file, index=False)
            
            print(f"Batch {batch_id}: Avg Humidity={avg_humidity_list[-1]:.2f}%, Max Humidity={max_humidity_list[-1]:.2f}%, Max Flow Rate={max_flow_rate_list[-1]:.2f} LPM, Avg Motor Speed={avg_motor_speed_list[-1]:.2f} RPM, Max Power={max_power_consumption_list[-1]:.2f} kW, Max Pressure={max_pressure_list[-1]:.2f} Bar")
        except Exception as e:
            print(f"Error processing Batch_{batch_id}.csv: {e}")
            avg_humidity_list.append(None)
            max_humidity_list.append(None)
            avg_flow_rate_list.append(None)
            max_flow_rate_list.append(None)
            avg_motor_speed_list.append(None)
            avg_compression_force_list.append(None)
            max_power_consumption_list.append(None)
            max_pressure_list.append(None)
            avg_vibration_list.append(None)
            max_vibration_list.append(None)
    else:
        print(f"Warning: Batch_{batch_id}.csv not found")
        avg_humidity_list.append(None)
        max_humidity_list.append(None)
        avg_flow_rate_list.append(None)
        max_flow_rate_list.append(None)
        avg_motor_speed_list.append(None)
        avg_compression_force_list.append(None)
        max_power_consumption_list.append(None)
        max_pressure_list.append(None)
        avg_vibration_list.append(None)
        max_vibration_list.append(None)

# Add the new columns to the summary dataframe
summary_df['Avg_Humidity_Percent'] = avg_humidity_list
summary_df['Max_Humidity_Percent'] = max_humidity_list
summary_df['Avg_Flow_Rate_LPM'] = avg_flow_rate_list
summary_df['Max_Flow_Rate_LPM'] = max_flow_rate_list
summary_df['Avg_Motor_Speed_RPM'] = avg_motor_speed_list
summary_df['Avg_Compression_Force_kN'] = avg_compression_force_list
summary_df['Max_Power_Consumption_kW'] = max_power_consumption_list
summary_df['Max_Pressure_Bar'] = max_pressure_list
summary_df['Avg_Vibration_mm_s'] = avg_vibration_list
summary_df['Max_Vibration_mm_s'] = max_vibration_list

# Remove the Phases column if it exists
if 'Phases' in summary_df.columns:
    summary_df = summary_df.drop(columns=['Phases'])

# Save the updated Summary.csv
summary_df.to_csv(r'/Users/suhaas/Machine-Learning/manu-sus-engine/Summary.csv', index=False)
print("\nSummary.csv has been updated with new columns!")
print(f"Updated Summary.csv shape: {summary_df.shape}")
print("\nFirst few rows with new columns:")
print(summary_df[['Batch_ID', 'Avg_Humidity_Percent', 'Max_Humidity_Percent', 'Avg_Flow_Rate_LPM', 'Max_Flow_Rate_LPM', 'Avg_Motor_Speed_RPM', 'Max_Power_Consumption_kW', 'Max_Pressure_Bar', 'Avg_Vibration_mm_s', 'Max_Vibration_mm_s']].head(10))
