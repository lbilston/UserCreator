
# This script should be run nightly to update the system with any new users, deactivating old accounts and ensuring staff are in the right groups.
# Export from HRMS system, using the following format
# employeeID, firstName, surname, department, startDate, endDate, status,

# import all required library
import csv
import subprocess
import sys
from datetime import datetime
import requests

# Clear the Screen
subprocess.run(['clear'])

# Function to import CSV and parse the file
def process_csv(filename):
    today = datetime.today().date()

    with open(filename, 'r') as csvfile, open('passwords.txt', 'a') as password_file:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #Assign each column to a variable
            employee_id = row['employeeID']
            first_name = row['firstName']
            surname = row['surname']
            department = row['department']
            start_date_str = row['startDate']
            end_date_str = row['endDate']
            status = row['status'].upper()  # Convert status to uppercase for easier comparison
            fullname = str(f" {first_name} {surname}")


            # Check if the date format is valid.  Needs to be in the format of dd/mm/yyyy
            try:
                start_date = datetime.strptime(start_date_str, '%d/%m/%Y').date()
                end_date = datetime.strptime(end_date_str, '%d/%m/%Y').date() if end_date_str else None
            except ValueError:
                print(f"Invalid date format for employee {employee_id}. Skipping. (dd/mm/yyyy)")
                continue
            # Creates a username based on firstname.lastname
            username = f"{first_name.lower()}.{surname.lower()}"

            # Only process the statement IF the account is ACTV and the date is greater than or equal to today
            if status == 'ACTV' and start_date <= today and (end_date is None or end_date >= today):
                # Check if user already exists
                user_exists = subprocess.call(['id', '-u', username], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

                #If the User exists, then create the user using linux commands useradd and chpasswd
                if not user_exists:

                    print(f"Creating User {username}")

                    # Use DinoPass to generate a Strong Password
                    passwordapi = 'http://www.dinopass.com/password/strong'
                    passwordrequest = requests.get(url=passwordapi)
                    statuscode = int(passwordrequest.status_code)

                    if statuscode == 200:
                        password = str(passwordrequest.text)

                        # Create and activate user
                        subprocess.run(['useradd', '-c', f"{first_name} {surname} ({department})", '-m', username])

                        # Set password
                        echo_process = subprocess.run(['echo', f"{username}:{password}"], stdout=subprocess.PIPE,text=True)
                        subprocess.run(['chpasswd'], input=echo_process.stdout, text=True)

                        # Save password to file
                        password_file.write(f"{first_name} {surname}, {employee_id}, {password}\n")

                    else:
                        print(f"Failed to generate password for employee {employee_id}. Skipping.")
                else:
                    # Ensure the existing user is active
                    print(f"Activating User {username}")
                    subprocess.run(['usermod', '-U', username])
                    subprocess.run(['usermod', '-U', '-a', '-G',  department, username])
                    subprocess.run(['usermod', '-c', fullname, username])

            elif status == 'LEFT' or (end_date is not None and end_date < today):
                # Deactivate user if end date is blank or less than today.
                print(f"Deactivating User {username}")
                subprocess.run(['usermod', '-L', username])

# Checks if the right syntax is used
# python UserCreator.py <csv_filename>

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python UserCreator.py <csv_filename>")
        sys.exit(1)

    csv_filename = sys.argv[1]
    process_csv(csv_filename)