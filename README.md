<strong>Django Job Finding APP</strong>

A web styled app built with Django that allows you to link to the Indeed API and download the latest jobs based on the search requirements you have.

Why did I Build this?
<ol>
 	<li>I got tired of browsing through thousands of job descriptions from pages and pages of lists just to come across the one job that was relevant to me. There are numerous reasons so I’ll try to list them all below:
<ul>
 	<li>Be able to mark a company as not interested so I don’t have to see it ever again</li>
 	<li>Be able to mark a company as good, so that I can see its jobs highlighted</li>
 	<li>Be able to quickly see all the new jobs that I haven’t seen before without having to troll through thousands of other listings</li>
 	<li>Be able to search all my different types of filters with one click of a button such as location, keyword, etc</li>
 	<li>Be able to identify jobs I am interested in and also able to remove jobs I am not interested in</li>
 	<li>Be able to mark a job as applied for, got a response or even rejected for</li>
 	<li>Be able to keep a record of the actual job description on a database for referring to later</li>
 	<li>Be able to remove duplicate jobs that crept into the database from the same company</li>
 	<li>Be able to search jobs that are not through staffing agencies</li>
</ul>
</li>
</ol>
<strong>Getting Started</strong>

There are 2 components that will be required to get your own copy of this project up and running.

A SQL database

The Django installation
<h2>Notes on setting up the SQL database:</h2>
I opted to use the PYODBC python module for communicating with a Microsoft sql database. I realise Django has a built in sql component, but I wanted to practice my skills with SQL and the actual SQL queries were getting a little complex.

There are a few resources online for helping you get set up with a local SQL database and this readme will not go into the specifics for how to do that. To get you started here is a good YouTube video that I found rather helpful

<a href="https://www.youtube.com/watch?v=yasfZuou3zI">https://www.youtube.com/watch?v=yasfZuou3zI</a>

Once you have setup your SQL server you will need to create the tables as follows:

--reed jobs, each job board has its own table

CREATE TABLE Reed_jobs (

job_id VARCHAR(100),

employer_name VARCHAR(100),

employer_profile_id INT,

employer_profile_name VARCHAR(100),

employer_id INT,

job_title VARCHAR(200),

actual_location VARCHAR(100),

salary VARCHAR(50),

min_salary INT,

max_salary INT,

currency VARCHAR(10),

expires DATE,

creation_date DATE,

short_description VARCHAR(1000),

long_description VARCHAR(8000),

applications INT,

internal_url VARCHAR(200),

external_url VARCHAR(2000),

removed VARCHAR(10),

PrIMARY KEY (job_id)

);

&nbsp;

--user searches, the parameters used in a particular type of search

CREATE TABLE User_searches (

search_query_num int NOT NULL IDENTITY(1,1),

user_id VARCHAR(100) NOT NULL,

search_keywords VARCHAR(100),

search_location VARCHAR(100),

search_distance INT,

search_permanent VARCHAR(10),

search_employers_only VARCHAR(100),

search_reed VARCHAR(10),

search_indeed VARCHAR(10),

lastIndeedFetchDate DATE,

PRIMARY KEY (search_query_num),

CONSTRAINT FK_user_id FOREIGN KEY (user_id) REFERENCES Users(user_id)

);

&nbsp;

--the users details

CREATE TABLE Users (

user_id VARCHAR(100),

first_name VARCHAR(100),

last_name VARCHAR(100),

PRIMARY KEY (user_id)

);

&nbsp;

--links the users searches, jobs, and if they like the job and have applied for it

--used to show all the users jobs on one screen from different boards

--later i need to include indeed and linkedin job ids as FK's

CREATE TABLE User_jobs (

job_number int NOT NULL IDENTITY(1,1),

user_id VARCHAR(100) NOT NULL,

search_query_num INT NOT NULL,

like_the_job VARCHAR(10),

applied VARCHAR(10),

the_status VARCHAR(10),

user_job_id VARCHAR(100),

PRIMARY KEY (job_number),

CONSTRAINT FK_user_id_user_jobs FOREIGN KEY (user_id) REFERENCES Users(user_id),

CONSTRAINT FK_search_query_num FOREIGN KEY (search_query_num) REFERENCES User_searches(search_query_num),

);

&nbsp;

--Table used for saying if user likes a specific company or not

CREATE TABLE User_companies (

unique_entry INT NOT NULL IDENTITY (1,1),

user_id VARCHAR(100) NOT NULL,

company_name VARCHAR(100) NOT NULL,

like_or_not VARCHAR(10),

PRIMARY KEY (unique_entry),

CONSTRAINT FK_comp_user_id_users_user_id FOREIGN KEY (user_id) REFERENCES Users(user_id),

);