import pandas as pd
import re
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the CSV file
df = pd.read_csv("D:/django/edit 2/vaultspace/users/tests/99acres.csv")

# Function to convert "Lac" values to numbers
def convert_rent(rent):
    rent = str(rent).replace("₹", "").strip()  # Remove currency symbol

    # Convert "Lac" to numerical lakh format
    if "Lac" in rent:
        number = re.findall(r"[\d.]+", rent)  # Extract numeric value
        if number:
            return float(number[0]) * 100000  # Convert Lac to Lakh numbering
    else:
        number = re.findall(r"[\d,]+", rent)  # Extract normal numbers
        if number:
            return int(number[0].replace(",", ""))  # Remove commas

    return rent  # Return as is if not matching

# Apply conversion to the rent column
df["rent"] = df["rent"].apply(convert_rent)

# Save the modified data back to CSV in current directory
output_csv = os.path.join(current_dir, "99acres_warehouse_rentals_updated.csv")
df.to_csv(output_csv, index=False)

print(f"Updated CSV saved in: {output_csv}")
