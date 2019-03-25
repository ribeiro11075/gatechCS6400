#################################################
##Author: David Ribeiro				#
##Date: 7/6/2018				#
##Purpose: Automate Database & Account Creation	#
##Assumption: Using MariaDB/MySQL		#
#################################################

#################################################
## Drop Database If Exists			#
## Create Database				#
#################################################

DROP DATABASE IF EXISTS cs6400;

CREATE DATABASE cs6400 CHARACTER SET UTF8;


#################################################
## Create User & Grant All Privileges		#
#################################################

GRANT ALL ON *.* TO cs6400@localhost IDENTIFIED BY 'cs6400';

#################################################
## Flush Privileges To Ensure They Take Affect	#
#################################################

FLUSH PRIVILEGES;
