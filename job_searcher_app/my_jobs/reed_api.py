#used to speak to the reed api for job searches
import requests
import pyodbc
import os
from datetime import datetime
from time import sleep
#This is the reed api-key
#we get the api key that is stored in environment variables in windows control panel
reed_api_key = os.environ.get('the_reed_api_key')

#create the pyodbc connection
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=DESKTOP-V2PBVUQ\SQLEXPRESS;'
                      'Database=Job_hunter;'
                      'Trusted_Connection=yes;')

def fetch_search_parameters(this_user, the_search_query_number):
	#fetches the users search query parmaters from database
	#cursor used to speak to database
	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM User_searches WHERE user_id = ? AND search_query_num = ?;""", this_user, the_search_query_number)
	row = cursor.fetchone()
	#add all the params to the temp dict so we can return them
	temp_dict = {'search_keywords': row.search_keywords,
					'search_location':row.search_location,
					'search_distance':row.search_distance,
					'search_permanent':row.search_permanent,
					'search_employers_only':row.search_employers_only,
					'search_reed':row.search_reed,
					'search_indeed':row.search_indeed}
	return temp_dict

def correct_the_date(wrong_format_date):
	#takes date dd/mm/yyyy and makes it yyyy-mm-dd
	if wrong_format_date != "":
		old_date = wrong_format_date
		day = old_date[0:2]
		month = old_date[3:5]
		year = old_date[6:10]
		new_date = year + "-" + month +"-" + day
		return new_date
	else:
		return wrong_format_date

def reed_job_summary(temp_params):
	
	#fetches the jobs based on the params from reed
	URL = "https://www.reed.co.uk/api/1.0/search?"
	#use this format for the paramaters
	the_parameters = {'resultsToTake':100,
					'keywords':temp_params['search_keywords'],
					'locationName':temp_params['search_location'],
					'distanceFromLocation':temp_params['search_distance'],
					'permanent':temp_params['search_permanent'],
					'postedByDirectEmployer':temp_params['search_employers_only']}
	
	
	"""
	#list of parameters that can be used
	employerId	        id of employer posting job
	employerProfileId	profile id of employer posting job
	keywords	        any search keywords
	locationName	    the location of the job
	distanceFromLocation	distance from location name in miles (default is 10)
	permanent	        true/false
	contract	        true/false
	temp	            true/false
	partTime	        true/false
	fullTime	        true/false
	minimumSalary	    lowest possible salary e.g. 20000
	maximumSalary	    highest possible salary e.g. 30000
	postedByRecruitmentAgency	true/false
	postedByDirectEmployer	true/false
	graduate	        true/false
	resultsToTake	    maximum number of results to return (defaults and is limited to 100 results)
	resultsToSkip	    number of results to skip (this can be used with resultsToTake for paging)
	"""	
	AUTH = "('username',reed_api_key)"
	r = requests.get(url = URL, params = the_parameters, auth = (reed_api_key,""))
	data = r.json()
	return data

def update_reed_jobs_table(reed_data):
	counter = 0
	#updates the reed table with the info from the reed api query
	#give data the correct names
	print(f'updating the reed database')
	for job in reed_data['results']:
		the_job_id = job["jobId"]
		the_employer_id = job["employerId"]
		the_employer_name = job["employerName"]
		the_employer_profile_id = job["employerProfileId"]
		the_employer_profile_name = job["employerProfileName"]
		the_job_title = job["jobTitle"]
		the_location = job["locationName"]
		the_min_sal = job["minimumSalary"]
		the_max_sal = job["maximumSalary"]
		the_currency = job["currency"]
		the_expiration_date = job["expirationDate"]
		the_date = job["date"]
		the_short_desc = job["jobDescription"]
		the_applications = job["applications"]
		the_job_url = job["jobUrl"]
		
		
		#check if jobid already in the database
		#cursor used to speak to database
		cursor = conn.cursor()
		cursor.execute("""SELECT job_id FROM Reed_jobs WHERE job_id = ?;""", the_job_id)
		row = cursor.fetchone()
		if not row:
			print(f'{the_job_id} not in reed database, so will add it')
			cursor.execute("""INSERT INTO Reed_jobs (	job_id,
														employer_name,
														employer_id,
														employer_profile_id,
														employer_profile_name,
														job_title,
														actual_location,
														min_salary,
														max_salary,
														currency,
														expires,
														creation_date,
														short_description,
														applications,
														internal_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);""", 
														the_job_id,
														the_employer_name,
														the_employer_id,
														the_employer_profile_id,
														the_employer_profile_name,
														the_job_title,
														the_location,
														the_min_sal,
														the_max_sal,
														the_currency,
														correct_the_date(the_expiration_date),
														correct_the_date(the_date),
														the_short_desc,
														the_applications,
														the_job_url)
		else:
			print(f'Already exists in the database')
		counter += 1
		print(f'Job number {counter} out of {reed_data["totalResults"]}')
	print(f'Updating reed database...')
	
	conn.commit()

def add_job_to_user_jobs(user_id, search_query_number, reed_data):
	#updates the user job table with the job info
	#cursor used to speak to database
	cursor = conn.cursor()
	for job in reed_data['results']:
		the_user_id = user_id
		the_search_query_num = search_query_number
		the_reed_job_id = job["jobId"]
		#check if jobid with the search query num is already in the database
		#cursor used to speak to database
		cursor = conn.cursor()
		cursor.execute(	"""SELECT user_job_id FROM User_jobs WHERE user_job_id = ? AND 
						search_query_num = ?;""", str(the_reed_job_id), the_search_query_num)
		row = cursor.fetchone()
		if not row:
			print(f'{the_reed_job_id} not in user jobs database, so will add it')
			cursor.execute("""INSERT INTO User_jobs (	user_job_id,
														user_id,
														search_query_num) VALUES (?,?,?);""",
														the_reed_job_id,
														the_user_id,
														the_search_query_num)
	conn.commit()

def reed_full_job_details():
	#this is for the full details
	#it requires a job_id, which you get from the search request
	job_id_list =[]
	counter = 0
	AUTH = "('username',reed_api_key)"
	#cursor used to speak to database
	cursor = conn.cursor()
	#first we make a list of jobs in the database with no long description
	print(f'Checking if any reed jobs dont have full details')
	for row in cursor.execute("""SELECT job_id FROM Reed_jobs WHERE long_description IS NULL;"""):
		job_id_list.append(row.job_id)
	print(f'There are {len(job_id_list)} jobs needing full details')
	for job in job_id_list:
		URL = f'https://www.reed.co.uk/api/1.0/jobs/{job}'
		r = requests.get(url = URL, auth = (reed_api_key,""))
		data = r.json()
		the_long_description = data['jobDescription']
		the_external_url = data['externalUrl']
#		print(the_long_description)
#		print(the_external_url)
		#cursor used to speak to database
		cursor = conn.cursor()
		cursor.execute("""UPDATE Reed_jobs SET long_description = ?,external_url = ? WHERE job_id = ?;""",the_long_description,the_external_url,job)
		conn.commit()
		counter += 1
		print(f'Completed {counter} out of {len(job_id_list)}')
		
		sleep(5)
	conn.commit()