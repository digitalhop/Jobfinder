from django.shortcuts import render
from django.http import HttpResponse
from my_jobs.database_comms import get_my_jobs, get_my_undecided_jobs, like_or_unlike_job, get_user_searches, update_job_searches, add_job_search, like_or_unlike_company, has_reed_job_been_removed, remove_user_jobs_when_user_search_removed, update_applied_status, update_feedback_status, get_active_searches_list, get_unliked_jobs, undo_unlike
from my_jobs.reed_api import fetch_search_parameters, correct_the_date, reed_job_summary, add_job_to_user_jobs, update_reed_jobs_table, reed_full_job_details

# Create your views here.
def index(request):
#	return HttpResponse('this works')
	return render(request, 'my_jobs/index.html')

#used for seeing the jobs that are liked
def jobs_view(request):
	if request.user.is_authenticated:
		#get username
		this_user = request.user.username
		#get requests
		if request.method == "GET":
			#run database function
			messages = get_my_jobs(this_user)
			context = { 'messages': messages }
			return render(request, 'my_jobs/index.html', context)
		elif request.method == "POST":
			#check which post request it is
			#is it the unlike job request
			if request.POST["choice"] == "nolikejob":
				#marks job as liked or not in user jobs table
				like_or_unlike_job("no", this_user, request.POST["userjobid"], request.POST["jobnumber"])
			elif request.POST["choice"] == "yeslikejob":
				#marks job as liked or not in user jobs table
				like_or_unlike_job("yes", this_user, request.POST["userjobid"], request.POST["jobnumber"])
			elif request.POST["choice"] == "markApplied":
				#marks job as applied in user jobs table
				update_applied_status(this_user, 'applied', request.POST["jobnumber"])
			elif request.POST["choice"] == "markDeclined":
				#marks job as rejected in user jobs table
				update_feedback_status(this_user, 'rejected', request.POST["jobnumber"])
			elif request.POST["choice"] == "markAccepted":
				#marks job as accepted in user jobs table
				update_feedback_status(this_user, 'accepted', request.POST["jobnumber"])
			#is it the like company request
			elif request.POST["choice"] == "yeslikecompany":
				like_or_unlike_company('yes', this_user, request.POST["companyname"])
			elif request.POST["choice"] == "nolikecompany":
				like_or_unlike_company('no', this_user, request.POST["companyname"])
			#run database function
			messages = get_my_jobs(this_user)
			context = { 'messages': messages }
			return render(request, 'my_jobs/index.html', context)
	else:
		return HttpResponse('not logged in')

#used for seeing the jobs that haven't been decided on yet
def jobs_undecided_view(request):
	if request.user.is_authenticated:
		#get username
		this_user = request.user.username
		#print(messages)
		#check if it was a post or get request
		if request.method == "GET":
			#run database function
			messages = get_my_undecided_jobs(this_user)
			context = { 'messages': messages }
		#    print(context)
			return render(request, 'my_jobs/undecided_jobs.html', context)
		#this post request is the like or not like job buttons
		elif request.method == "POST":
			#check which post request it is
			#is it the like job request
			if request.POST["choice"] == "yeslikejob":
				#marks job as liked or not in user jobs table
				like_or_unlike_job("yes", this_user, request.POST["userjobid"], request.POST["jobnumber"])
			elif request.POST["choice"] == "nolikejob":
				like_or_unlike_job("no", this_user, request.POST["userjobid"], request.POST["jobnumber"])
			#is it the like company request
			elif request.POST["choice"] == "yeslikecompany":
				like_or_unlike_company('yes', this_user, request.POST["companyname"])
			elif request.POST["choice"] == "nolikecompany":
				like_or_unlike_company('no', this_user, request.POST["companyname"])
			#run database function
			messages = get_my_undecided_jobs(this_user)
			context = { 'messages': messages }
			return render(request, 'my_jobs/undecided_jobs.html', context)
	else:
		return HttpResponse('not logged in')

def jobs_searches_view(request):
	#check if logged in
	if request.user.is_authenticated:
		#get username
		this_user = request.user.username
		#check if it was a post or get request
		if request.method == "GET":
			#run database function to get searches for user
			messages = get_user_searches(this_user)
			context = { 'messages': messages }
			return render(request, 'my_jobs/job_searches.html', context)
		elif request.method == "POST":
			#check if it is a delete search request
			if request.POST["delete_job"] == "yes":
				#run the delete search database query
				update_job_searches("delete", this_user, request.POST["searchnumber"])
				#remove associated user jobs from user jobs database
				remove_user_jobs_when_user_search_removed(this_user, request.POST["searchnumber"])	
			elif request.POST["delete_job"] == "no":
				#if it was a post request other than to remove a search
				#add the new search params to the database
				keyword = request.POST["keyword"]
				location = request.POST["location"]
				distance = request.POST["distance"]
				#if user selected permanent it will be 'on' in the request
				if "temp" in request.POST:
					temp_or_perm = "false"
				else:
					temp_or_perm = "true"
				if "employer" in request.POST:
					employers = "false"
				else:
					employers = "true"
				if "reed" in request.POST:
					reed = "yes"
				else:
					reed = "no"
				if "indeed" in request.POST:
					indeed = "yes"
				else:
					indeed = "no"
				add_job_search(this_user, keyword, location, distance, temp_or_perm, employers, reed, indeed)
			elif request.POST["delete_job"] == "nope":
				#get the search paramaters from user search database
				search_filters = fetch_search_parameters(this_user, request.POST["searchnumber"])
				#search the reed api with the parameters
				api_results = reed_job_summary(search_filters)
				#update the reed database with the new found jobs
				update_reed_jobs_table(api_results)
				#add the jobs to the user jobs database
				add_job_to_user_jobs(this_user, request.POST["searchnumber"], api_results)
				#need to also check if the jobs in reed api have been removed
				#and update reed job database if it has
				has_reed_job_been_removed(this_user, request.POST["searchnumber"], api_results)
				#get the full details for all jobs that don't have it in the database
				reed_full_job_details()
			elif request.POST["delete_job"] == "fetchall":
				#goes through all the users searches
				#we create a list of active searchnumbers and iterate through them
				active_searches = get_active_searches_list(this_user)
				#loop through active searches list
				for active_search in active_searches:
					print(f'the active search is: {active_search}')
					#get the search paramaters from user search database
					search_filters = fetch_search_parameters(this_user, active_search)
					#search the reed api with the parameters
					api_results = reed_job_summary(search_filters)
					#update the reed database with the new found jobs
					update_reed_jobs_table(api_results)
					#add the jobs to the user jobs database
					add_job_to_user_jobs(this_user, active_search, api_results)
					#need to also check if the jobs in reed api have been removed
					#and update reed job database if it has
					has_reed_job_been_removed(this_user, active_search, api_results)
					#get the full details for all jobs that don't have it in the database
					reed_full_job_details()
			messages = get_user_searches(this_user)
			context = { 'messages': messages }
			return render(request, 'my_jobs/job_searches.html', context)
	else:
		return HttpResponse('not logged in')

#used for seeing the jobs that a user has liked or unliked
def jobs_unliked(request):
	if request.user.is_authenticated:
		#get username
		this_user = request.user.username
		#print(messages)
		#check if it was a post or get request
		if request.method == "GET":
			#run database function
			messages = get_unliked_jobs(this_user)
			context = { 'messages': messages }
		#    print(context)
			return render(request, 'my_jobs/unliked_jobs.html', context)
		#this post request is the undo btn for a previously unliked job
		elif request.method == "POST":
			#check which post request it is
			if request.POST["choice"] == "yeslikejob":
				#undos previously unliked marked job 
				undo_unlike(this_user, request.POST["userjobid"])
			#run database function
			messages = get_unliked_jobs(this_user)
			context = { 'messages': messages }
			return render(request, 'my_jobs/unliked_jobs.html', context)
	else:
		return HttpResponse('not logged in')