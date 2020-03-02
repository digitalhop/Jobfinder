import pyodbc
from selenium import webdriver

#this script iterates through the manually enetered salary responses and allows user to 
#designate a number to them
#e.g. 0 for salary below 3500
#1 for salary above 3499

#create the pyodbc connection
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
						'Server=DESKTOP-V2PBVUQ\SQLEXPRESS;'
						'Database=Job_hunter;'
						'Trusted_Connection=yes;')

def indeed_raw_fetch_raw_salar_response():
    #if the salaryRespnse is not null or 'e', then we add it to a list with the file name
    #this will allow us to loop through this list and manually update the salaryResonse
    #with the normalised number
	cursor = conn.cursor()
	data_list = []
	for row in cursor.execute(	"""SELECT salaryResponse, raw_num_entry FROM Indeed_raw 
                                WHERE (salaryResponse != 'e' AND salaryResponse IS NOT NULL AND salaryNormalised IS NULL);"""):
                                data = {}
                                data.setdefault('raw_num_entry', row.raw_num_entry)
                                data.setdefault('salaryResponse', row.salaryResponse)
                                data_list.append(data)
	return data_list


def update_indeed_raw_salaryResponse(raw_number_entry, salaryResponse):
	#update salary response column
	cursor = conn.cursor()
	cursor.execute("""UPDATE Indeed_raw SET salaryNormalised = ? WHERE raw_num_entry = ?;""", salaryResponse, raw_number_entry)
	conn.commit()

def count_num_of_rows_with_salary_response():
    #so we can see how many we have done already
    cursor = conn.cursor()
    cursor.execute( """SELECT raw_num_entry FROM Indeed_raw WHERE (salaryResponse != 'e' AND salaryResponse IS NOT NULL AND salaryNormalised IS NULL);""")
    data = len(cursor.fetchall())
    return data


list_of_raw_salary = indeed_raw_fetch_raw_salar_response()

#loop through each row of data and ask for the salary info
for each_row in list_of_raw_salary:
    print(f'the number of salaries still to normalise: {count_num_of_rows_with_salary_response()}')
    print(f'the salary of: {each_row["salaryResponse"]}')
    new_salary_response = input("enter normalised salary here, or type 'exit' to quit ")
    if new_salary_response == 'exit':
        exit()
    else:
        update_indeed_raw_salaryResponse(each_row['raw_num_entry'], new_salary_response)
        continue

    