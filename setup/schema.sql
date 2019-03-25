#################################################
#Author: David Ribeiro				#
#Date: 7/6/2018					#
#Purpose: Automate Schema Build			#
#Assumption: Using MariaDB/MySQL		#
# - You have already run database_setup.sql
# - As a result cs6400 database is empty but exists
#################################################

#################################################
## Drop resource_requests Table If Exists	#
## Drop incidents Table If Exists		#
## Drop incident_types Table If Exists		#
## Drop resource_capabilities Table If Exists	#
## Drop resource_secondary_esfs Table If Exists	#
## Drop resources Table If Exists		#
## Drop esfs Table If Exists			#
## Drop cost_pers Table If Exists		#
## Drop companies Table If Exists		#
## Drop government_agencies Table If Exists	#
## Drop municipalities Table If Exists		#
## Drop individuals Table If Exists		#
## Drop users Table If Exists			#
## Drop companies Trigger If Exists		#
## Drop government_agencies Trigger If Exists	#
## Drop invididuals Trigger If Exists		#
## Drop municipalities Trigger If Exists	#
#################################################

USE cs6400
DROP TABLE IF EXISTS resource_requests;
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS incident_types;
DROP TABLE IF EXISTS resource_capabilities;
DROP TABLE IF EXISTS resource_secondary_esfs;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS esfs;
DROP TABLE IF EXISTS cost_pers;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS government_agencies;
DROP TABLE IF EXISTS municipalities;
DROP TABLE IF EXISTS individuals;
DROP TABLE IF EXISTS users;
DROP TRIGGER IF EXISTS companies_check_distinct_usernames;
DROP TRIGGER IF EXISTS government_agencies_check_distinct_usernames;
DROP TRIGGER IF EXISTS individuals_check_distinct_usernames;
DROP TRIGGER IF EXISTS municipalities_check_distinct_usernames;


#################################################
## Create users Table				#
#################################################

CREATE TABLE users (
username VARCHAR(100) NOT NULL,
password VARCHAR(100) NOT NULL,
name VARCHAR(100) NOT NULL,
CONSTRAINT pk_users_username PRIMARY KEY (username)
);


#################################################
## Create individuals Table			#
#################################################

CREATE TABLE individuals (
username VARCHAR(100) NOT NULL,
job_title VARCHAR(100) NOT NULL,
hire_date DATE NOT NULL,
CONSTRAINT pk_individuals_username PRIMARY KEY (username),
CONSTRAINT fk_individuals_username FOREIGN KEY (username)
REFERENCES users (username)
);


#################################################
## Create municipalities Table			#
#################################################

CREATE TABLE municipalities (
username VARCHAR(100) NOT NULL,
category VARCHAR(100) NOT NULL,
CONSTRAINT pk_municipalities_username PRIMARY KEY (username),
CONSTRAINT fk_municipalities_username FOREIGN KEY (username)
REFERENCES `users` (username)
);


#################################################
## Create government_agencies Table		#
#################################################

CREATE TABLE government_agencies (
username VARCHAR(100) NOT NULL,
agency_name_local_office VARCHAR(100) NOT NULL,
CONSTRAINT pk_government_agencies_username PRIMARY KEY (username),
CONSTRAINT fk_government_agencies_username FOREIGN KEY (username)
REFERENCES `users` (username)
);


#################################################
## Create companies Table			#
#################################################

CREATE TABLE companies (
username VARCHAR(100) NOT NULL,
hq_location VARCHAR(100) NOT NULL,
num_employees INT NOT NULL,
CONSTRAINT pk_companies_username PRIMARY KEY (username),
CONSTRAINT fk_companies_username FOREIGN KEY (username)
REFERENCES `users` (username)
);


#################################################
## Create cost_pers Table			#
#################################################

CREATE TABLE cost_pers (
cost_per VARCHAR(100) NOT NULL,
CONSTRAINT pk_cost_pers_cost_per PRIMARY KEY (cost_per)
);


#################################################
## Create esfs Table				#
#################################################

CREATE TABLE esfs (
esf_id INT NOT NULL,
description VARCHAR(100) NOT NULL,
CONSTRAINT pk_esfs_esf_id PRIMARY KEY (esf_id)
);


#################################################
## Create resources Table			#
#################################################

CREATE TABLE resources (
resource_id INT NOT NULL AUTO_INCREMENT,
owner VARCHAR(100) NOT NULL,
name VARCHAR(100) NOT NULL,
availability_status VARCHAR(100) NOT NULL DEFAULT 'Available',
latitude DECIMAL(8,6) NOT NULL,
longitude DECIMAL(9,6) NOT NULL,
model VARCHAR(250) DEFAULT NULL,
cost DECIMAL(10,2) NOT NULL,
cost_per VARCHAR(100) NOT NULL,
maximum_distance DECIMAL(10,2) DEFAULT NULL,
primary_esf_id INT NOT NULL,
CONSTRAINT ck_resources_status CHECK (availability_status IN ('Available', 'In Use')),
CONSTRAINT pk_resources_resource_id PRIMARY KEY (resource_id),
CONSTRAINT fk_resources_primary_esf FOREIGN KEY (primary_esf_id)
REFERENCES esfs (esf_id),
CONSTRAINT fk_resources_cost_per FOREIGN KEY (cost_per)
REFERENCES cost_pers (cost_per),
CONSTRAINT fk_resources_username FOREIGN KEY (owner)
        REFERENCES users (username)
);


#################################################
## Create resource_secondary_esfs Table		#
#################################################

CREATE TABLE resource_secondary_esfs (
resource_id INT NOT NULL,
esf_id INT NOT NULL,
CONSTRAINT pk_resource_secondary_esfs_resource_id_esf_id PRIMARY KEY (resource_id, esf_id),
CONSTRAINT fk_resource_secondary_esfs_esf_id FOREIGN KEY (esf_id)
REFERENCES esfs (esf_id),
CONSTRAINT fk_resource_secondary_esfs_resource_id FOREIGN KEY (resource_id)
        REFERENCES resources (resource_id)
);


#################################################
## Create resource_capabilities Table		#
#################################################

CREATE TABLE resource_capabilities(
resource_id INT NOT NULL,
capability VARCHAR(100) NOT NULL,
CONSTRAINT pk_resource_capabilities_resource_id_capability PRIMARY KEY (resource_id , capability ),
CONSTRAINT fk_resource_capabilities_resource_id FOREIGN KEY (resource_id)
        REFERENCES resources (resource_id)
);


#################################################
## Create incident_types Table			#
#################################################

CREATE TABLE incident_types (
abbreviation VARCHAR(100) NOT NULL,
description VARCHAR(100) NOT NULL,
CONSTRAINT pk_incident_types_abbreviation PRIMARY KEY (abbreviation)
);


#################################################
## Create incidents Table			#
#################################################

CREATE TABLE incidents (
abbreviation VARCHAR(100) NOT NULL,
incident_id INT NOT NULL,
owner VARCHAR(100) NOT NULL,
incident_date DATE NOT NULL,
description VARCHAR(100) NOT NULL,
latitude DECIMAL(8,6) NOT NULL,
longitude DECIMAL(9,6) NOT NULL,
CONSTRAINT pk_incidents_abbreviation_incident_id PRIMARY KEY (abbreviation, incident_id),
CONSTRAINT fk_incidents_abbreviation FOREIGN KEY (abbreviation)
        REFERENCES incident_types (abbreviation),
CONSTRAINT fk_incidents_owner FOREIGN KEY (owner)
        REFERENCES users (username)
);


#################################################
## Create resource_requests Table		#
#################################################

CREATE TABLE resource_requests(
request_id INT NOT NULL AUTO_INCREMENT,
resource_id INT NOT NULL,
abbreviation varchar(100) NOT NULL,
incident_id INT NOT NULL,
requested_start_date DATE NOT NULL,
expected_return_date DATE NOT NULL,
request_accepted_deploy_date DATE DEFAULT NULL,
request_status VARCHAR(100) NOT NULL DEFAULT  'Pending',
PRIMARY KEY pk_resource_requests_request_id (request_id),
CONSTRAINT ck_resource_requests_start_return_date CHECK (requested_start_date <= expected_return_date),
CONSTRAINT ck_resource_requests_request_status CHECK (request_status IN ('Pending', 'Deployed', 'Rejected', 'Canceled', 'Completed')),
CONSTRAINT fk_resource_requests_resource_id FOREIGN KEY (resource_id)
        REFERENCES resources (resource_id),
CONSTRAINT fk_resource_requests_abbreviation_incident_id FOREIGN KEY (abbreviation, incident_id)
        REFERENCES incidents (abbreviation, incident_id)
);


#################################################
## Create companies Trigger			#
#################################################

DELIMITER |
create trigger companies_check_distinct_usernames
        before insert on companies
for each row
BEGIN
        if new.username in
                (select username from government_agencies union select username from municipalities union select username from individuals)
        THEN SIGNAL SQLSTATE '45000' set MESSAGE_TEXT = 'Username already exists in another subclass of the user superclass'; END IF;
END |
DELIMITER ;


#################################################
## Create government_agencies Trigger		#
#################################################

DELIMITER |
create trigger government_agencies_check_distinct_usernames
        before insert on government_agencies
for each row
BEGIN
        if new.username in
                (select username from companies union select username from municipalities union select username from individuals)
        THEN SIGNAL SQLSTATE '45000' set MESSAGE_TEXT = 'Username already exists in another subclass of the user superclass'; END IF;
END |
DELIMITER ;


#################################################
## Create individuals Trigger			#
#################################################

DELIMITER |
create trigger individuals_check_distinct_usernames
        before insert on individuals
for each row
BEGIN
        if new.username in
                (select username from government_agencies union select username from companies union select username from municipalities)
        THEN SIGNAL SQLSTATE '45000' set MESSAGE_TEXT = 'Username already exists in another subclass of the user superclass'; END IF;
END |
DELIMITER ;


#################################################
## Create municipalities Trigger		#
#################################################

DELIMITER |
create trigger municipalities_check_distinct_usernames
        before insert on municipalities
for each row
BEGIN
        if new.username in
                (select username from government_agencies union select username from companies union select username from individuals)
        THEN SIGNAL SQLSTATE '45000' set MESSAGE_TEXT = 'Username already exists in another subclass of the user superclass'; END IF;
END |
DELIMITER ;
