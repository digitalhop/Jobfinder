#holds the functions used to retrieve and werite data to database
import pyodbc
import os
from datetime import datetime
from django.contrib.auth.models import User

#create the pyodbc connection
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
						'Server=DESKTOP-V2PBVUQ\SQLEXPRESS;'
						'Database=Job_hunter;'
						'Trusted_Connection=yes;')

'''def has_date_passed(the_date):
	#checks to see if a date has passed todays date
	#returns 'passed' if date has passed
	#sql_date = datetime.strptime(str(the_date), '%y-%m-%d')
	present_date = datetime.now().date()
	if present_date > the_date:
		return 'passed'
	else:
		return 'stillgood'

def date_expired_class(passed_or_not):
	#check if the date has expired
	#this is to make the class red or green
	if passed_or_not == "passed":
		return 'dateExpired'
	else:
		return 'dateNotExpired'
'''
def applied_or_nope_class(status):
	#depending on the application status from the user jobs
	#this deals with the applied or not class
	if status is None:
		return 'grey'
	elif status == 'applied':
		return 'green'

def applied_status_class(status):
	#depending on the application status from the user jobs
	#this deals with the accepted or not class
	if status is None:
		return 'grey'
	elif status == 'accepted':
		return 'green'

def like_or_not_class(like_or_not):
	#depending on the current data base status of the job
	#returns the class for the icon
	if like_or_not == 'yes':
		return 'green'
	elif like_or_not is None:
		return 'grey'
	else:
		return 'red'

def get_my_jobs(this_user):
	#used for the my liked jobs view
	cursor = conn.cursor()
	messages = []
	for row in cursor.execute(	"""SELECT * FROM (	SELECT * FROM Indeed_jobs UNION ALL SELECT * FROM Reed_jobs) AS BIG
								RIGHT JOIN User_jobs ON User_jobs.user_job_id = Big.job_id
								LEFT JOIN User_searches ON User_searches.search_query_num = User_jobs.search_query_num
								LEFT JOIN User_companies ON User_companies.company_name = BIG.employer_name
								WHERE (User_jobs.user_id = ? AND User_jobs.like_the_job = ?)
								AND (User_jobs.the_status IS NULL OR User_jobs.the_status = ?);""", this_user, 'yes', 'accepted'):
		emp_name = row.employer_name
		like_company = row.like_or_not
		jobid = row.job_id
		jobnumber = row.job_number
		jobtitle = row.job_title
		location = row.actual_location
		min_sal = row.min_salary
		if min_sal == None:
			min_sal = 'Not given'
		max_sal = row.max_salary
		if max_sal == None:
			max_sal = 'Not given'
		exp = row.expires
		created = row.creation_date
		shor_des = row.short_description
		long_des = row.long_description
		apps = row.applications
		reedurl = row.internal_url
		exturl = row.external_url
		search_query = row.search_query_num
		likejob = row.like_the_job
		appliedyet = row.applied
		status = row.the_status
		keyword = row.search_keywords
		user_job_id = row.user_job_id
		messages.append({	'employer_name':emp_name,
							'like_company_class':like_or_not_class(like_company),
							'job_id':jobid,
							'job_title':jobtitle,
							'actual_location':location,
							'min_salary':min_sal,
							'max_salary':max_sal,
							'job_number':jobnumber,
							'expires':exp,
							#we check if the date has passed and then return the class
							#'date_expired_checker':date_expired_class(has_date_passed(exp)),
							'creation_date':created,
							'short_description':shor_des,
							'long_description':long_des,
							'applications':apps,
							'search_query_num':search_query,
							'search_keyword':keyword,
							'like_the_job':like_or_not_class(likejob),
							#need to return separate classes for the accepted and applied icons
							'applied':applied_or_nope_class(appliedyet),
							'status':applied_status_class(status),
							'user_job_id':user_job_id,
							'reed_url':reedurl})    


	return messages

def get_my_undecided_jobs(this_user):
	#used for the jobs view to get all jobs that have not been decided
	cursor = conn.cursor()
	messages = []
	for row in cursor.execute(	"""SELECT * FROM (	SELECT * FROM Indeed_jobs UNION ALL SELECT * FROM Reed_jobs) AS BIG
								RIGHT JOIN User_jobs ON User_jobs.user_job_id = Big.job_id
								LEFT JOIN User_searches ON User_searches.search_query_num = User_jobs.search_query_num
								LEFT JOIN User_companies ON User_companies.company_name = BIG.employer_name
								WHERE (User_jobs.user_id = ? AND User_jobs.like_the_job IS NULL)
								AND (User_companies.like_or_not IS NULL or User_companies.like_or_not = 'yes')
								AND (BIG.expires > GETDATE() AND BIG.removed IS NULL OR BIG.expires IS NULL);""", this_user):
		emp_name = row.employer_name
		jobnumber = row.job_number
		jobid = row.job_id
		jobtitle = row.job_title
		location = row.actual_location
		min_sal = row.min_salary
		if min_sal == None:
			min_sal = 'Not given'
		max_sal = row.max_salary
		if max_sal == None:
			max_sal = 'Not given'
		exp = row.expires
		created = row.creation_date
		shor_des = row.short_description
		long_des = row.long_description
		apps = row.applications
		reedurl = row.internal_url
		exturl = row.external_url
		search_query = row.search_query_num
		keyword = row.search_keywords
		likejob = row.like_the_job
		like_comp = row.like_or_not
		appliedyet = row.applied
		user_job_id = row.user_job_id

		messages.append({	'employer_name':emp_name, 
							'job_id':jobid,
							'job_title':jobtitle,
							'actual_location':location,
							'min_salary':min_sal,
							'max_salary':max_sal,
							'expires':exp,
							'creation_date':created,
							'short_description':shor_des,
							'long_description':long_des,
							'applications':apps,
							'search_query_num':search_query,
							'search_keyword':keyword,
							'like_the_job':likejob,
							'like_the_company':like_or_not_class(like_comp),
							'applied':appliedyet,
							'reed_url':reedurl,
							'job_url':exturl,
							'user_job_id':user_job_id,
							'job_number':jobnumber})    
	return messages

def old_like_or_unlike_job(like_or_unlike, this_user, user_job_id):
	'''marks a job as liked in user jobs table, if the job is already liked
	and the user requests liked again, then we give it a status of null'''
	#get the latest like status
	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM User_jobs WHERE user_id = ? AND user_job_id = ?;""", this_user, user_job_id)
	row = cursor.fetchone()
	if row:
		#is it a reverse like request
		if row.like_the_job == 'yes' and like_or_unlike == 'yes':
			cursor = conn.cursor()
			cursor.execute("""UPDATE User_jobs SET like_the_job = ? WHERE job_number = ? AND user_id = ?;""", None, job_number, this_user)
			conn.commit()
		#update the job
		else:
			cursor = conn.cursor()
			cursor.execute("""UPDATE User_jobs SET like_the_job = ? WHERE job_number = ? AND user_id = ?;""", like_or_unlike, job_number, this_user)
			conn.commit()

def like_or_unlike_job(like_or_unlike, this_user, user_job_id, request_job_number):
	'''marks a job as liked in user jobs table, if the job is already liked
	and the user requests liked again, then we give it a status of null'''
	#get the latest like status
	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM User_jobs WHERE user_id = ? AND job_number = ?;""", this_user, request_job_number)
	row = cursor.fetchone()
	if row.like_the_job == 'yes' and like_or_unlike == 'yes':
		job_numbers = []
		for row in cursor.execute("""SELECT * FROM User_jobs WHERE user_id = ? AND user_job_id = ?;""", this_user, user_job_id):
			job_numbers.append(row.job_number)
		for job_number in job_numbers:
			cursor.execute("""UPDATE User_jobs SET like_the_job = ? WHERE job_number = ? AND user_id = ?;""", None, job_number, this_user)
	elif row.like_the_job == 'yes' and like_or_unlike == 'no':
		job_numbers = []
		for row in cursor.execute("""SELECT * FROM User_jobs WHERE user_id = ? AND user_job_id = ?;""", this_user, user_job_id):
			job_numbers.append(row.job_number)
		for job_number in job_numbers:
			cursor.execute("""UPDATE User_jobs SET like_the_job = ? WHERE job_number = ? AND user_id = ?;""", 'no', job_number, this_user)
	elif row.like_the_job is None and like_or_unlike == 'yes':
		job_numbers = []
		for row in cursor.execute("""SELECT * FROM User_jobs WHERE user_id = ? AND user_job_id = ?;""", this_user, user_job_id):
			job_numbers.append(row.job_number)
		for job_number in job_numbers:
			cursor.execute("""UPDATE User_jobs SET like_the_job = ? WHERE job_number = ? AND user_id = ?;""", 'yes', job_number, this_user)
	elif row.like_the_job is None and like_or_unlike == 'no':
		job_numbers = []
		for row in cursor.execute("""SELECT * FROM User_jobs WHERE user_id = ? AND user_job_id = ?;""", this_user, user_job_id):
			job_numbers.append(row.job_number)
		for job_number in job_numbers:
			cursor.execute("""UPDATE User_jobs SET like_the_job = ? WHERE job_number = ? AND user_id = ?;""", 'no', job_number, this_user)
	conn.commit()

def like_or_unlike_company(like_or_unlike, this_user, company_name):
	#marks a job as liked in user jobs table
	#check if company already has been liked or not
	cursor = conn.cursor()
	print('starting')
	cursor.execute(	"""SELECT * FROM User_companies WHERE user_id = ?
								AND company_name =  ?;""", this_user, company_name)
	row = cursor.fetchone()
	#if the cmpany doesn't have the like or not set
	if not row:
		cursor.execute("""INSERT INTO User_companies VALUES (?, ?, ?);""", this_user, company_name, like_or_unlike)
		conn.commit()
	#reverse like company 
	elif row.like_or_not == 'yes' and like_or_unlike == 'yes':
		cursor.execute(	"""DELETE FROM User_companies WHERE like_or_not = ?
						AND company_name = ? AND user_id = ?;""", like_or_unlike, company_name, this_user)
		conn.commit()
	#reverse company unlike
	elif row.like_or_not == 'no' and like_or_unlike == 'no':
		cursor.execute(	"""DELETE FROM User_companies WHERE like_or_not = ?
						AND company_name = ? AND user_id = ?;""", like_or_unlike, company_name, this_user)
		conn.commit()

	#unlike company that was previously liked
	elif row.like_or_not == 'yes' and like_or_unlike == 'no':
		cursor.execute(	"""UPDATE User_companies SET like_or_not = ?
						WHERE company_name = ? AND user_id = ?""", like_or_unlike, company_name, this_user)
		conn.commit()
	
	#like company that was previously unliked
	elif row.like_or_not == 'no' and like_or_unlike == 'yes':
		cursor.execute(	"""UPDATE User_companies SET like_or_not = ?
						WHERE company_name = ? AND user_id = ?""", like_or_unlike, company_name, this_user)
		conn.commit()

def get_user_searches(this_user):
	#fetches the latest searches for a particular user
	cursor = conn.cursor()
	messages = []
	for row in cursor.execute(	"""SELECT * FROM User_searches 
								WHERE user_id = ? and search_is_active IS NULL;""", this_user):
		sear_num = row.search_query_num
		sear_keys = row.search_keywords
		sear_loc = row.search_location
		sear_dist = row.search_distance
		sear_perm = row.search_permanent
		sear_empl_only = row.search_employers_only
		sear_read = row.search_reed
		sear_indeed = row.search_indeed
		
		messages.append({	'search_query_num':sear_num, 
							'search_keywords':sear_keys,
							'search_location':sear_loc,
							'search_distance':sear_dist,
							'search_permanent':sear_perm,
							'search_employers_only':sear_empl_only,
							'search_reed':sear_read,
							'search_indeed':sear_indeed})    
	return messages

def get_active_searches_list(this_user):
	#creates a list of active searches
	list_of_active_searches = []
	cursor = conn.cursor()
	for row in cursor.execute("""SELECT search_query_num FROM User_searches 
		WHERE user_id = ? and search_is_active IS NULL;""", this_user):
			list_of_active_searches.append(row.search_query_num)
	return list_of_active_searches

def update_job_searches(add_or_delete, this_user, search_num):
	#removes a search or adds a new one depending on if the user
	#selected to delete or they entered in new search query
	#check if it is a delete request first
	if add_or_delete == "delete":
		
		cursor = conn.cursor()
		cursor.execute("""UPDATE User_searches SET search_is_active = ? WHERE user_id =?
						AND search_query_num =?;""", "no", this_user, search_num)
		conn.commit()

def add_job_search(this_user, keyword, location=None, distance=None, temp_or_perm=None, employers=None, reed=None, indeed=None, is_active=None):
	#adds a new search query to the user database
	cursor = conn.cursor()
	cursor.execute("""INSERT INTO User_searches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""", this_user, keyword, location, distance, temp_or_perm, employers, reed, indeed, is_active)
	conn.commit()

def has_reed_job_been_removed(this_user, search_num, reed_api_data):
	'''checks if a user search returned a result that now doesn't
	contain a reed job id that was associated with this search before
	we then mark the job as removed on the reed jobs database'''
	#get a list of job ids from previous search
	previous_job_search_ids = []
	cursor = conn.cursor()
	for row in cursor.execute(	"""SELECT search_query_num, user_job_id, User_jobs.user_id, removed FROM User_jobs
								INNER JOIN Reed_jobs ON Reed_jobs.job_id = User_jobs.user_job_id
								WHERE (User_jobs.user_id = ? AND User_jobs.search_query_num = ?)
								AND Reed_jobs.removed IS NULL;""", this_user, search_num):
		if row:
			previous_job_search_ids.append(row.user_job_id)
	#build a list of job ids that still exist on reed api
	current_job_search_ids = []
	for jobs in reed_api_data['results']:
		if 'jobId' in jobs:
			current_job_search_ids.append(str(jobs["jobId"]))
	#create list of job ids that are not in the reed api list
	#but are in the reed job database
	#print(f'list of jobs in database: {previous_job_search_ids}')
	#print(f'list of jobs in reed search: {current_job_search_ids}')
	removed_reed_jobs = []
	for jobs in previous_job_search_ids:
		if jobs not in current_job_search_ids:
			cursor = conn.cursor()
			cursor.execute(	"""UPDATE Reed_jobs SET removed ='yes' WHERE job_id = ?;""", jobs)
	conn.commit()

def remove_user_jobs_when_user_search_removed(this_user, search_num):
	'''when a user deletes a search we also need to remove the jobs
	associated with that particular search from the users jobs database
	we also don't want to remove a job that the user likes or doesn't like'''
	cursor = conn.cursor()
	cursor.execute(	"""DELETE FROM User_jobs WHERE user_id = ? AND search_query_num = ?
					AND like_the_job IS NULL;""", this_user, search_num)
	conn.commit()

def update_applied_status(this_user, new_status, job_number):
	'''updates the user applied status either applied or reverse applied status'''

	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM User_jobs WHERE user_id = ? AND job_number = ?;""", this_user, job_number)
	row = cursor.fetchone()
	if row:
		#is this a new status for the application
		if row.applied is None:
			cursor = conn.cursor()
			cursor.execute("""UPDATE User_jobs SET applied = ? WHERE user_id =?
					AND job_number =?;""", new_status, this_user, job_number)
			conn.commit()
		#is this a reverse of applied request
		elif row.applied == 'applied' and new_status == 'applied':
			cursor = conn.cursor()
			cursor.execute("""UPDATE User_jobs SET applied = NULL WHERE user_id =?
					AND job_number =?;""", this_user, job_number)
			conn.commit()

def update_feedback_status(this_user, new_status, job_number):
	'''updates the user applied status either accepted, or rejected or reverse accepted'''

	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM User_jobs WHERE user_id = ? AND job_number = ?;""", this_user, job_number)
	row = cursor.fetchone()
	if row:
		#is this a new status for the application
		if row.the_status is None:
			cursor = conn.cursor()
			cursor.execute("""UPDATE User_jobs SET the_status = ? WHERE user_id =?
					AND job_number =?;""", new_status, this_user, job_number)
			conn.commit()
		#is this a reverse of applied request
		elif row.the_status == 'accepted' and new_status == 'accepted':
			cursor = conn.cursor()
			cursor.execute("""UPDATE User_jobs SET the_status = NULL WHERE user_id =?
					AND job_number =?;""", this_user, job_number)
			conn.commit()
		#is this a reverse of applied request
		elif row.the_status == 'accepted' and new_status == 'rejected':
			cursor = conn.cursor()
			cursor.execute("""UPDATE User_jobs SET the_status = 'rejected' WHERE user_id =?
					AND job_number =?;""", this_user, job_number)
			conn.commit()

def insert_linked_in_raw_data(url, html):
	#inserts url with params and html job details into
	#Linkedin_raw database
	cursor = conn.cursor()
	cursor.execute("""INSERT INTO Linkedin_raw VALUES (?, ?);""", url, html)
	conn.commit()