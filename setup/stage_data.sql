#############################################################
##Author: David Ribeiro				#
##Date: 7/6/2018				#
##Purpose: Automate Data Creation		#
##Assumption: Using MariaDB/MySQL		#
# - You have already run database_setup.sql
# - As a result cs6400 database is empty but exists
# - You have also run schema.sql
# - As a result 13 empty base tables were created in cs6400
#############################################################

# Make sure you are in the right database
use cs6400;

## users
INSERT INTO users VALUES ('testindividual', 'cs6400', 'Test Individual');
INSERT INTO users VALUES ('testcompany', 'cs6400', 'Test Company');
INSERT INTO users VALUES ('testmunicipality', 'cs6400', 'Test Municipality');
INSERT INTO users VALUES ('testgovernmentagency', 'cs6400', 'Test Government Agency');


## user details
INSERT INTO individuals VALUES ('testindividual', 'Data Entry', '1992-03-27');
INSERT INTO companies VALUES ('testcompany', 'Washington DC', 1000);
INSERT INTO municipalities VALUES ('testmunicipality', 'City');
INSERT INTO government_agencies VALUES ('testgovernmentagency', 'FBI - Atlanta Office');


## cost_pers
INSERT INTO cost_pers VALUES ('hour');
INSERT INTO cost_pers VALUES ('day');
INSERT INTO cost_pers VALUES ('week');
INSERT INTO cost_pers VALUES ('each');


## esfs
INSERT INTO esfs VALUES (1, 'Transportation');
INSERT INTO esfs VALUES (2, 'Communications');
INSERT INTO esfs VALUES (3, 'Public Works and Engineering');
INSERT INTO esfs VALUES (4, 'Firefighting');
INSERT INTO esfs VALUES (5, 'Emergency Management');
INSERT INTO esfs VALUES (6, 'Mass Care, Emergency Assistance, Housing, and Human Services');
INSERT INTO esfs VALUES (7, 'Logistics Management and Resource Support');
INSERT INTO esfs VALUES (8, 'Public Health and Medical Services');
INSERT INTO esfs VALUES (9, 'Search and Rescue');
INSERT INTO esfs VALUES (10, 'Oil and Hazardous Materials Response');
INSERT INTO esfs VALUES (11, 'Agriculture and Natural Resources');
INSERT INTO esfs VALUES (12, 'Energy');
INSERT INTO esfs VALUES (13, 'Public Safety and Security');
INSERT INTO esfs VALUES (14, 'Long-Term Community Recovery');
INSERT INTO esfs VALUES (15, 'External Affairs');


## incident_types
INSERT INTO incident_types VALUES ('MD', 'Major Disaster Declaration');
INSERT INTO incident_types VALUES ('ED', 'Emergency Declaration');
INSERT INTO incident_types VALUES ('FM', 'Fire Management Assistance');
INSERT INTO incident_types VALUES ('FS', 'Fire Suppression Authorization');


## testindividual resources
INSERT INTO resources (owner, name, availability_status, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testindividual', 'Leo''s Ladder', 'In Use', 38.9, 77, 10, 'day', 100, 1);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testindividual', 'Fire Truck', 38.8, 77, 10, 'day', 10, 2);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testindividual', 'Ambulance', 39, 77, 10, 'day', 50, 3);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testindividual', 'Police Car', 38.9, 77, 10, 'day', 25000, 4);


## testcompany resources
INSERT INTO resources (owner, name, availability_status, latitude, longitude, model, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testcompany', 'Will''s Little Giant', 'In Use', 38.9, 77, 'Ladder', 10, 'hour', 100, 5);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testcompany', 'Google Fire Truck', 38.8, 77, 10, 'hour', 10, 6);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testcompany', 'Google Ambulance', 39, 77, 10, 'hour', 50, 7);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testcompany', 'Google Police Car', 38.9, 77, 10, 'hour', 25000, 8);


## testmunicipality resources
INSERT INTO resources (owner, name, availability_status, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testmunicipality', 'Peter''s Fire Truck', 'In Use', 38.9, 77, 10, 'week', 100, 9);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testmunicipality', 'DC Fire Truck', 38.8, 77, 10, 'week', 10, 10);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testmunicipality', 'DC Ambulance', 39, 77, 10, 'week', 50, 11);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testmunicipality', 'DC Police Car', 38.9, 77, 10, 'week', 25000, 12);


## testgovernmentagency resources
INSERT INTO resources (owner, name, availability_status, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testgovernmentagency', 'Peter''s Other Fire Truck', 'In Use', 38.9, 77, 10, 'each', 100, 13);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testgovernmentagency', 'FBI Fire Truck', 38.8, 77, 10, 'each', 10, 14);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testgovernmentagency', 'FBI Ambulance', 39, 77, 10, 'each', 50, 15);

INSERT INTO resources (owner, name, latitude, longitude, cost, cost_per, maximum_distance, primary_esf_id) VALUES('testgovernmentagency', 'FBI Police Car', 38.9, 77, 10, 'each', 25000, 1);


## Peters Fire Truck Capability
INSERT INTO resource_capabilities VALUES (9, 'Ladder');


## Incidents
INSERT INTO incidents VALUES ('MD', 1, 'testindividual', '2018-07-23', 'Volcano', 39, 77);
INSERT INTO incidents VALUES ('MD', 2, 'testindividual', '2018-07-23', 'Volcano', 39, 77);

INSERT INTO incidents VALUES ('ED', 1, 'testcompany', '2018-07-23', 'Tornado', 38.8, 77);
INSERT INTO incidents VALUES ('ED', 2, 'testcompany', '2018-07-23', 'Tornado', 38.8, 77);

INSERT INTO incidents VALUES ('FM', 1, 'testmunicipality', '2018-07-23', 'House Fire', 36, 77);
INSERT INTO incidents VALUES ('FM', 2, 'testmunicipality', '2018-07-23', 'House Fire', 36, 77);

INSERT INTO incidents VALUES ('FS', 1, 'testgovernmentagency', '2018-07-23', 'Car Fire', 30, 77);
INSERT INTO incidents VALUES ('FS', 2, 'testgovernmentagency', '2018-07-23', 'Car Fire', 30, 77);


## Resource Requests In Use

INSERT INTO resource_requests (resource_id, abbreviation, incident_id, requested_start_date, expected_return_date, request_accepted_deploy_date, request_status) VALUES (1, 'ED', 1, '2018-07-24', '2018-07-30', '2018-07-24', 'Deployed');

INSERT INTO resource_requests (resource_id, abbreviation, incident_id, requested_start_date, expected_return_date, request_accepted_deploy_date, request_status) VALUES (5, 'FM', 1, '2018-07-24', '2018-07-30', '2018-07-24', 'Deployed');

INSERT INTO resource_requests (resource_id, abbreviation, incident_id, requested_start_date, expected_return_date, request_accepted_deploy_date, request_status) VALUES (9, 'FS', 1, '2018-07-24', '2018-07-30', '2018-07-24', 'Deployed');

INSERT INTO resource_requests (resource_id, abbreviation, incident_id, requested_start_date, expected_return_date, request_accepted_deploy_date, request_status) VALUES (13, 'MD', 1, '2018-07-24', '2018-07-30', '2018-07-24', 'Deployed');


## Resource Requests Pending

INSERT INTO resource_requests (resource_id, abbreviation, incident_id, requested_start_date, expected_return_date) VALUES (2, 'ED', 1, '2018-07-24', '2018-07-30');

INSERT INTO resource_requests (resource_id, abbreviation, incident_id, requested_start_date, expected_return_date) VALUES (6, 'FM', 1, '2018-07-24', '2018-07-30');

INSERT INTO resource_requests (resource_id, abbreviation, incident_id, requested_start_date, expected_return_date) VALUES (10, 'FS', 1, '2018-07-24', '2018-07-30');

INSERT INTO resource_requests (resource_id, abbreviation, incident_id, requested_start_date, expected_return_date) VALUES (14, 'MD', 1, '2018-07-24', '2018-07-30');
