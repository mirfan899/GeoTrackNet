from datetime import datetime, timedelta

# Define the date range
start_date = datetime(2024, 3, 18)
end_date = datetime(2024, 10, 30)

# Calculate the total number of days
total_days = (end_date - start_date).days + 1

# Define split ratios
train_ratio = 0.7
val_ratio = 0.15
test_ratio = 0.15

# Calculate days for each split
train_days = int(total_days * train_ratio)
val_days = int(total_days * val_ratio)
test_days = total_days - train_days - val_days  # Remaining days

# Generate split dates
train_end_date = start_date + timedelta(days=train_days - 1)
val_end_date = train_end_date + timedelta(days=val_days)
test_end_date = val_end_date + timedelta(days=test_days)

# Print results
print("Train: {} to {}".format(start_date.strftime("%d-%m-%Y"), train_end_date.strftime("%d-%m-%Y")))
print("Validation: {} to {}".format((train_end_date + timedelta(days=1)).strftime("%d-%m-%Y"), val_end_date.strftime("%d-%m-%Y")))
print("Test: {} to {}".format((val_end_date + timedelta(days=1)).strftime("%d-%m-%Y"), test_end_date.strftime("%d-%m-%Y")))
