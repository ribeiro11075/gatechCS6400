def login_select_users(cursor, username):
	query = "SELECT password FROM users WHERE UPPER(username) = %s"
	cursor.execute(query, (username.upper(), ))
	query_result = cursor.fetchall()

	if not query_result:
		return None

	return query_result[0][0]


def menu_select_user_details(cursor, username):
	query = "SELECT A.name, B.top_line, B.bottom_line FROM users A INNER JOIN (SELECT username AS username, CONCAT('Location: ', hq_location) AS top_line, CONCAT('Number of Employees: ', num_employees) AS bottom_line FROM companies UNION SELECT username AS username, category AS top_line, NULL FROM municipalities UNION SELECT username AS username, CONCAT('Job Title: ', job_title) AS top_line, CONCAT('Hire Date: ', hire_date) AS bottom_line FROM individuals UNION SELECT username AS username, agency_name_local_office AS top_line, NULL FROM government_agencies) B ON A.username = B.username WHERE A.username = %s"
	cursor.execute(query, (username.upper(), ))
	query_result = cursor.fetchall()
	
	return query_result[0]



def resource_select_cost_pers(cursor):
	query = "SELECT cost_per FROM cost_pers"
	cursor.execute(query)
	query_result = cursor.fetchall()

	return [cost_per[0] for cost_per in query_result]


def resource_select_esfs(cursor):
	query = "SELECT esf_id, description FROM esfs"
	cursor.execute(query)
	query_result = cursor.fetchall()

	return dict(query_result)


def check_primary_esf_field(cursor, primary_esf_id):
	query = "SELECT COUNT(*) FROM esfs WHERE esf_id = %s"
	cursor.execute(query, (primary_esf_id, ))
	query_result = cursor.fetchall()

	if query_result[0][0] == 0:
		return None

	return query_result


def check_cost_per_field(cursor, cost_per):
	query = "SELECT COUNT(*) FROM cost_pers WHERE cost_per = %s"
	cursor.execute(query, (cost_per, ))
	query_result = cursor.fetchall()

	if query_result[0][0] == 0:
		return None

	return query_result


def check_secondary_esf_field(cursor, secondary_esfs):
	esf_ids = ', '.join(["'" + esf_id + "'" for esf_id in secondary_esfs])
	query = "SELECT COUNT(*) FROM esfs WHERE esf_id in (" + esf_ids + ")"
	cursor.execute(query)
	query_result = cursor.fetchall()

	if len(secondary_esfs) != query_result[0][0]:
		return None

	return query_result


def resource_add_resource(cursor, conn, username, resource_name, latitude, longitude, model, cost, cost_per, max_distance, primary_esf_id):
	query = "INSERT INTO resources (owner, name, latitude, longitude, model, cost, cost_per, maximum_distance, primary_esf_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
	cursor.execute(query, (username, resource_name, latitude, longitude, model, cost, cost_per, max_distance, primary_esf_id))

	query = "SELECT LAST_INSERT_ID()"
	cursor.execute(query)
	resource_id = cursor.fetchall()[0][0]
	conn.commit()

	return resource_id


def resource_add_capabilities(cursor, conn, resource_id, capability):
	query  = "INSERT INTO resource_capabilities (resource_id, capability) VALUES (%s, %s)"
	cursor.execute(query, (resource_id, capability))
	conn.commit()


def resource_add_secondary_esfs(cursor, conn, resource_id, esf_id):
	query = "INSERT INTO resource_secondary_esfs (resource_id, esf_id) VALUES (%s, %s)"
	cursor.execute(query, (resource_id, esf_id))
	conn.commit()


def incident_select_incident_types(cursor):
	query = "SELECT abbreviation, description FROM incident_types"
	cursor.execute(query)
	query_result = cursor.fetchall()

	return dict(query_result)


def search_select_esfs(cursor):
	query = "SELECT esf_id, description FROM esfs"
	cursor.execute(query)
	query_result = cursor.fetchall()

	return dict(query_result)


def search_select_incidents(cursor, username):
	query = "select CONCAT(abbreviation, '-', incident_id) as id, description from incidents where owner = %s"
	cursor.execute(query, (username))
	query_result = cursor.fetchall()

	return query_result


def results_select_resources(cursor, username, keyword, esf_id, incident_id, abbreviation, location, criteria="none"):
	qry_none =		"""
				SELECT A.resource_id, A.name, A.owner, A.cost, A.availability_status, COALESCE(B.expected_return_date, 'NOW') as expected_return_date,
					A.cost_per, 0 AS distance, 'N' as button_id
				FROM
				resources A
				LEFT JOIN
				(SELECT resource_id, expected_return_date FROM resource_requests WHERE request_status ='Deployed') B
				ON A.resource_id = B.resource_id
				ORDER BY name ASC
				"""

	qry_loc =		"""
				SELECT FINAL.resource_id, FINAL.name, FINAL.owner, FINAL.cost, FINAL.availability_status, COALESCE(RETURN_DATE.expected_return_date, 'NOW') as expected_return_date,
					FINAL.cost_per, CAST(FINAL.distance as decimal(40,1)) as distance, CASE WHEN FINAL.owner = %s and FINAL.availability_status = 'Available' THEN 'D'
					WHEN FINAL.owner = %s and FINAL.availability_status = 'In Use' THEN 'U' WHEN C.status is not null then C.status else 'R' END as button_id
				FROM
				(SELECT A.resource_id, A.name, A.owner, A.cost, A.cost_per, A.availability_status, A.maximum_distance, B.distance FROM resources A
					INNER JOIN
					(SELECT resource_id, (2 * ATAN2(SQRT(a), SQRT(1-a))) * 6373 AS distance FROM (SELECT POWER(SIN(dlat / 2),2) + COS(lat1) * COS(lat2) * POWER(sin(dlon
						/ 2), 2) AS a, dlat, dlon, lat1, lat2, lon1, lon2, resource_id FROM (select lat2 - lat1 AS
						dlat, lon2 - lon1 AS dlon, lat1, lat2, lon1, lon2, resource_id FROM (SELECT
						RADIANS(A.latitude) AS lat1, RADIANS(B.latitude) AS lat2, RADIANS(A.longitude)
						AS lon1, RADIANS(B.longitude) AS lon2, B.resource_id AS resource_id FROM
						incidents  A,  resources B WHERE A.incident_id = %s AND A.abbreviation =%s) X) Y) Z) B
					ON A.resource_id = B.resource_id
					WHERE B.distance <= %s ) FINAL
				LEFT JOIN
				(select resource_id, expected_return_date FROM resource_requests WHERE request_status ='Deployed') RETURN_DATE
				ON FINAL.resource_id = RETURN_DATE.resource_id
				LEFT JOIN

				(select Z.resource_id, CASE WHEN Z.request_status = 'Deployed' THEN 'CD' WHEN Z.request_status = 'Pending' THEN 'CP' ELSE 'C' END as status

					from resource_requests Z

					INNER JOIN incidents Y

					ON Z.abbreviation = Y.abbreviation and Z.incident_id = Y.incident_id
					INNER JOIN resources X
					on X.resource_id = Z.resource_id

					WHERE request_status in ('Deployed', 'Pending', 'Completed') and Y.owner = %s and X.owner <> %s) C

				ON FINAL.resource_id = C.resource_id
				WHERE FINAL.maximum_distance >= FINAL.distance
				ORDER BY distance ASC, name ASC
				"""

	qry_noloc_key = 	"""
				SELECT A.resource_id, A.name, A.owner, A.cost, A.availability_status, COALESCE(B.expected_return_date, 'NOW') as expected_return_date,
					A.cost_per, 0 AS distance, 'N' as button_id
				FROM
				resources A
				LEFT JOIN
				(SELECT resource_id, expected_return_date FROM resource_requests WHERE request_status = 'Deployed') B
				ON A.resource_id = B.resource_id
				WHERE A.resource_id IN (
					SELECT A.resource_id FROM resources A
					LEFT JOIN
					resource_capabilities B
					ON A.resource_id = B.resource_id
					WHERE A.name LIKE %s OR A.model LIKE %s OR B.capability LIKE %s)
				ORDER BY name ASC
				"""

	qry_noloc_esf = 	"""
				SELECT A.resource_id, A.name, A.owner, A.cost, A.availability_status, COALESCE(B.expected_return_date, 'NOW') as expected_return_date,
					A.cost_per, 0 AS distance, 'N' as button_id
				FROM
				resources A
				LEFT JOIN
				(SELECT resource_id, expected_return_date FROM  resource_requests WHERE request_status = 'Deployed') B
				ON A.resource_id = B.resource_id
				WHERE A.resource_id IN (
					SELECT resource_id FROM resources WHERE primary_esf_id = %s
					UNION
					SELECT resource_id FROM resource_secondary_esfs WHERE esf_id = %s)
				ORDER BY  name ASC
				"""

	qry_noloc_key_esf = 	"""
				SELECT A.resource_id, A.name, A.owner, A.cost, A.availability_status, COALESCE(B.expected_return_date, 'NOW') as expected_return_date,
					A.cost_per, 0 as distance, 'N' as button_id
				FROM resources A
				LEFT JOIN
				(SELECT resource_id, expected_return_date FROM  resource_requests WHERE request_status = 'Deployed') B
				ON A.resource_id = B.resource_id
				WHERE A.resource_id IN (
					SELECT Y.resource_id FROM resources Y
					LEFT JOIN
					resource_capabilities Z
					ON Y.resource_id = Z.resource_id
					WHERE Y.name LIKE %s OR Y.model LIKE %s OR Z.capability LIKE %s)
				AND A.resource_id IN
					(SELECT resource_id FROM resources WHERE primary_esf_id = %s
					UNION
					SELECT resource_id FROM resource_secondary_esfs WHERE esf_id = %s)
				ORDER BY  name ASC
				"""
## Includes locations
	qry_loc_key_inc =	"""
				SELECT CORE.resource_id, CORE.name, CORE.owner, CORE.cost, CORE.availability_status, COALESCE(RETURN_DATE.expected_return_date, 'NOW') as expected_return_date,
					cost_per, CAST(DISTANCE.distance as decimal(40,1)) as distance, CASE WHEN CORE.owner = %s and CORE.availability_status = 'Available' THEN 'D'
					WHEN CORE.owner = %s and CORE.availability_status = 'In Use' THEN 'U' WHEN C.status is not null then C.status else 'R' END as button_id
				FROM
				(SELECT resource_id, name, owner, cost, availability_status, maximum_distance FROM resources
					WHERE resource_id IN
						(SELECT A.resource_id FROM resources A
						LEFT JOIN
						resource_capabilities B
						ON A.resource_id = B.resource_id
						WHERE A.name LIKE %s OR A.model LIKE %s OR B.capability LIKE %s)) CORE
				INNER JOIN
				(SELECT resource_id, name, owner, cost, availability_status, cost_per, distance FROM
					(SELECT A.resource_id, A.name, A.owner, A.cost, A.availability_status, cost_per, B.distance FROM resources A
					INNER JOIN
					(SELECT resource_id, (2 * ATAN2(SQRT(a), SQRT(1-a))) * 6371 AS distance FROM (SELECT POWER(SIN(dlat / 2),2) +
						COS(lat1) * COS(lat2) * POWER(sin(dlon / 2), 2) AS a, dlat, dlon, lat1, lat2, lon1, lon2,
						resource_id FROM (select lat2 - lat1 AS dlat, lon2 - lon1 AS dlon, lat1, lat2, lon1, lon2,
						resource_id FROM (SELECT RADIANS(A.latitude) AS lat1, RADIANS(B.latitude) AS
						lat2, RADIANS(A.longitude) AS lon1, RADIANS(B.longitude) AS lon2, B.resource_id
						AS resource_id FROM  incidents  A, resources B WHERE A.incident_id = %s
						AND A.abbreviation = %s ) X) Y) Z) B
					ON A.resource_id = B.resource_id
					WHERE B.distance <= %s ) Z) DISTANCE
				ON CORE.resource_id = DISTANCE.resource_id
				LEFT JOIN (select resource_id, expected_return_date FROM resource_requests WHERE request_status ='Deployed') RETURN_DATE
								ON CORE.resource_id = RETURN_DATE.resource_id
				LEFT JOIN

				(select Z.resource_id, CASE WHEN Z.request_status = 'Deployed' THEN 'CD' WHEN Z.request_status = 'Pending' THEN 'CP' ELSE 'C' END as status

					from resource_requests Z

					INNER JOIN incidents Y

					ON Z.abbreviation = Y.abbreviation and Z.incident_id = Y.incident_id
					INNER JOIN resources X
					on X.resource_id = Z.resource_id

					WHERE request_status in ('Deployed', 'Pending', 'Completed') and Y.owner = %s and X.owner <> %s) C

				ON CORE.resource_id = C.resource_id
				WHERE CORE.maximum_distance >= DISTANCE.distance
				ORDER BY distance ASC, name ASC
				"""

	qry_loc_esf_inc =	"""
				SELECT CORE.resource_id, CORE.name, CORE.owner, CORE.cost, CORE.availability_status, COALESCE(RETURN_DATE.expected_return_date, 'NOW') as expected_return_date,
					cost_per, CAST(DISTANCE.distance as decimal(40,1)) as distance, CASE WHEN CORE.owner = %s and CORE.availability_status = 'Available' THEN 'D'
					WHEN CORE.owner = %s and CORE.availability_status = 'In Use' THEN 'U' WHEN C.status is not null then C.status else 'R' END as button_id
				FROM
				(SELECT resource_id, name, owner, cost, availability_status, maximum_distance FROM resources
					WHERE resource_id IN
						(SELECT resource_id FROM resources WHERE primary_esf_id = %s
						UNION
						SELECT resource_id FROM resource_secondary_esfs WHERE esf_id = %s )) CORE
				INNER JOIN
				(SELECT resource_id, name, owner, cost, availability_status, cost_per, distance FROM
					(SELECT A.resource_id, A.name, A.owner, A.cost, A.availability_status, cost_per, B.distance FROM resources A
					INNER JOIN
					(SELECT resource_id, (2 * ATAN2(SQRT(a), SQRT(1-a))) * 6371 AS distance FROM (SELECT POWER(SIN(dlat / 2),2) +
						COS(lat1) * COS(lat2) * POWER(sin(dlon / 2), 2) AS a, dlat, dlon, lat1, lat2, lon1, lon2,
						resource_id FROM (select lat2 - lat1 AS dlat, lon2 - lon1 AS dlon, lat1, lat2, lon1, lon2,
						resource_id FROM (SELECT RADIANS(A.latitude) AS lat1, RADIANS(B.latitude) AS
						lat2, RADIANS(A.longitude) AS lon1, RADIANS(B.longitude) AS lon2, B.resource_id
						AS resource_id FROM  incidents  A, resources B WHERE A.incident_id = %s
						AND A.abbreviation = %s ) X) Y) Z) B
					ON A.resource_id = B.resource_id
					WHERE B.distance <= %s ) Z) DISTANCE
				ON CORE.resource_id = DISTANCE.resource_id
				LEFT JOIN (select resource_id, expected_return_date FROM resource_requests WHERE request_status ='Deployed') RETURN_DATE
				ON CORE.resource_id = RETURN_DATE.resource_id
				LEFT JOIN

				(select Z.resource_id, CASE WHEN Z.request_status = 'Deployed' THEN 'CD' WHEN Z.request_status = 'Pending' THEN 'CP' ELSE 'C' END as status

					from resource_requests Z

					INNER JOIN incidents Y

					ON Z.abbreviation = Y.abbreviation and Z.incident_id = Y.incident_id
					INNER JOIN resources X
					on X.resource_id = Z.resource_id

					WHERE request_status in ('Deployed', 'Pending', 'Completed') and Y.owner = %s and X.owner <> %s) C

				ON CORE.resource_id = C.resource_id
				WHERE CORE.maximum_distance >= DISTANCE.distance
				ORDER BY distance ASC, name ASC
				"""

	qry_loc_key_esf_inc =	"""
				SELECT CORE.resource_id, CORE.name, CORE.owner, CORE.cost, CORE.availability_status, COALESCE(RETURN_DATE.expected_return_date, 'NOW') as expected_return_date,
					CORE.cost_per, CAST(DISTANCE.distance as decimal(40,1)) as distance, CASE WHEN CORE.owner = %s and CORE.availability_status = 'Available' THEN 'D'
					WHEN CORE.owner = %s and CORE.availability_status = 'In Use' THEN 'U' WHEN C.status is not null then C.status else 'R' END as button_id
				FROM
				(SELECT resource_id, name, owner, cost, availability_status, maximum_distance FROM resources
					WHERE resource_id IN
						(SELECT A.resource_id FROM  resources A
						LEFT JOIN
						resource_capabilities B
						ON A.resource_id = B.resource_id
						WHERE A.name LIKE %s OR A.model LIKE %s OR B.capability LIKE %s)
					AND resource_id IN
						(SELECT resource_id FROM resources WHERE primary_esf_id = %s
						UNION
						SELECT resource_id FROM resource_secondary_esfs WHERE esf_id = %s )) CORE
				INNER JOIN
				(SELECT resource_id, name, owner, cost, availability_status, cost_per, distance FROM
					(SELECT A.resource_id, A.name, A.owner, A.cost, A.availability_status, cost_per, B.distance FROM resources A
					INNER JOIN
					(SELECT resource_id, (2 * ATAN2(SQRT(a), SQRT(1-a))) * 6371 AS distance FROM (SELECT POWER(SIN(dlat / 2),2) +
						COS(lat1) * COS(lat2) * POWER(sin(dlon / 2), 2) AS a, dlat, dlon, lat1, lat2, lon1, lon2,
						resource_id FROM (select lat2 - lat1 AS dlat, lon2 - lon1 AS dlon, lat1, lat2, lon1, lon2,
						resource_id FROM (SELECT RADIANS(A.latitude) AS lat1, RADIANS(B.latitude) AS
						lat2, RADIANS(A.longitude) AS lon1, RADIANS(B.longitude) AS lon2, B.resource_id
						AS resource_id FROM  incidents  A, resources B WHERE A.incident_id = %s
						AND A.abbreviation = %s ) X) Y) Z) B
					ON A.resource_id = B.resource_id
					WHERE B.distance <= %s ) Z) DISTANCE
				ON CORE.resource_id = DISTANCE.resource_id
				LEFT JOIN (select resource_id, expected_return_date FROM resource_requests WHERE request_status ='Deployed') RETURN_DATE
				ON CORE.resource_id = RETURN_DATE.resource_id
				LEFT JOIN

				(select Z.resource_id, CASE WHEN Z.request_status = 'Deployed' THEN 'CD' WHEN Z.request_status = 'Pending' THEN 'CP' ELSE 'C' END as status

					from resource_requests Z

					INNER JOIN incidents Y

					ON Z.abbreviation = Y.abbreviation and Z.incident_id = Y.incident_id
					INNER JOIN resources X
					on X.resource_id = Z.resource_id

					WHERE request_status in ('Deployed', 'Pending', 'Completed') and Y.owner = %s and X.owner <> %s) C

				ON CORE.resource_id = C.resource_id
				WHERE CORE.maximum_distance >= DISTANCE.distance
				ORDER BY distance ASC, name ASC
				"""

	# search query conditional
	#----------------------------
	if criteria == "none":
		cursor.execute(qry_none)
	elif criteria == "loc":
		cursor.execute(qry_loc, (username, username, incident_id, abbreviation, location, username, username))
	elif criteria == "inc":
		cursor.execute(qry_loc, (username, username, incident_id, abbreviation, location, username, username))
	elif criteria == "noloc-key":
		cursor.execute(qry_noloc_key, (keyword, keyword, keyword))
	elif criteria == "noloc-esf":
		cursor.execute(qry_noloc_esf, (esf_id, esf_id))
	elif criteria == "noloc-key-esf":
		cursor.execute(qry_noloc_key_esf, (keyword, keyword, keyword, esf_id, esf_id))
	elif criteria == "loc-key-inc":
		cursor.execute(qry_loc_key_inc, (username, username, keyword, keyword, keyword, incident_id, abbreviation, location, username, username))
	elif criteria == "loc-esf-inc":
		cursor.execute(qry_loc_esf_inc, (username, username, esf_id, esf_id, incident_id, abbreviation, location, username, username))
	elif criteria == "loc-key-esf-inc":
		cursor.execute(qry_loc_key_esf_inc, (username, username, keyword, keyword, keyword, esf_id, esf_id, incident_id, abbreviation, location, username, username))
	elif criteria == 'invalid':
		cursor.execute(qry_loc_key_esf_inc, ('invalid', 'invalid', 'invalid', -1, -1, -1, 'XY', location,'invalid','invalid') )

	query_result = cursor.fetchall()

	return query_result


def results_request_resource(cursor, conn, resource_id, abbreviation, incident_id, requested_start_date, expected_return_date):
	query = "INSERT INTO resource_requests(resource_id, abbreviation, incident_id, requested_start_date, expected_return_date) VALUES (%s, %s, %s, %s, %s)"
	cursor.execute(query, (int(resource_id), abbreviation, int(incident_id), requested_start_date, expected_return_date))
	conn.commit()


#################################
# Old version of deploy		#
#################################
def results_deploy_resource(cursor, conn, resource_id, abbreviation, incident_id, expected_return_date):
	# Old version of deploy
	#-------------------------
	query = "UPDATE resources SET availability_status = 'In Use' WHERE resource_id = %s"
	query2= """INSERT INTO  resource_requests(resource_id, abbreviation, incident_id, requested_start_date, expected_return_date, request_accepted_deploy_date,request_status) 
			VALUES ( %s,  %s , %s, NOW(),%s, NOW(), %s)"""

	def execute_both():
		cursor.execute(query, (resource_id))
		cursor.execute(query2, (resource_id,  abbreviation , incident_id , expected_return_date, 'Deployed'))

	execute_both()
	conn.commit()

##################################################
# New version of deploy - No longer needed?		#
##################################################
def results_deploy_resource2(cursor, conn, request_id, resource_id):
	query = "UPDATE resources SET availability_status = 'In Use' WHERE resource_id = %s"
	query2= "UPDATE resource_requests SET request_accepted_deploy_date = NOW(), request_status = 'Deployed' WHERE request_id = %s"

	def execute_both():
		cursor.execute(query, (resource_id))
		cursor.execute(query2, (request_id))

	execute_both()
	conn.commit()


def status_select_inuse(cursor, username):
	qry =	"""
		SELECT A.request_id, A.resource_id, C.name, B.description, C.owner, A.requested_start_date, A.expected_return_date
		FROM resource_requests A
		INNER JOIN incidents B
		ON A.abbreviation = B.abbreviation and A.incident_id = B.incident_id
		INNER JOIN resources C
		ON A.resource_id = C.resource_id
		WHERE C.availability_status = 'In Use' AND A.request_status='Deployed' AND B.owner = %s
		"""

	cursor.execute(qry, (username.upper()))
	qry_result = cursor.fetchall()

	return qry_result


def status_select_myrequests(cursor, username):
	qry = 	"""
		SELECT A.request_id, A.resource_id, C.name, B.description, C.owner, A.requested_start_date, A.expected_return_date
		FROM resource_requests A
		INNER JOIN incidents B
		ON A.abbreviation = B.abbreviation and A.incident_id = B.incident_id
		INNER JOIN resources C
		ON A.resource_id = C.resource_id
		WHERE A.request_status = 'Pending' AND B.owner =%s
		"""

	cursor.execute(qry, (username.upper()))
	qry_result = cursor.fetchall()

	return qry_result


def status_select_myresponses(cursor, username):
	qry =	"""
		SELECT A.request_id, A.resource_id, C.name, B.description, B.owner,
			A.requested_start_date, A.expected_return_date, CASE WHEN C.availability_status = 'In Use' THEN 'U' ELSE 'D' END as button_id
		FROM resource_requests A
		INNER JOIN incidents B
		ON A.abbreviation = B.abbreviation and A.incident_id = B.incident_id
		INNER JOIN resources C
		ON A.resource_id = C.resource_id
		WHERE A.request_status = 'Pending' AND C.owner = %s
		"""

	cursor.execute(qry, (username.upper()))
	qry_result = cursor.fetchall()

	return qry_result


def status_return_resource(cursor, conn, request_id, resource_id):
	qry1 = "UPDATE resource_requests SET request_status = 'Completed' WHERE request_id = %s"
	qry2 = "UPDATE resources  SET availability_status = 'Available' WHERE resource_id = %s"

	def doboth():
		cursor.execute(qry1, (request_id))
		cursor.execute(qry2, (resource_id))
		return None

	doboth()
	conn.commit()


def status_cancel_request(cursor, conn, request_id):
	qry = "UPDATE resource_requests SET request_status = 'Cancelled' WHERE request_id = %s"

	cursor.execute(qry, (request_id))
	conn.commit()


def status_check_availability(cursor, resource_id,):
	q_checkuse = "SELECT 1 FROM resources WHERE availability_status = 'In Use' AND resource_id = %s"
	cursor.execute(q_checkuse, (resource_id,))
	query_result = cursor.fetchall()

	if query_result:
		return 1
	else:
		return 0

	return query_result


def status_deploy_resource(cursor, conn, request_id, resource_id, expected_return_date):
	query = "UPDATE resources SET availability_status = 'In Use' WHERE resource_id = %s"
	query2= "UPDATE resource_requests SET request_accepted_deploy_date = NOW(), request_status = 'Deployed' WHERE request_id = %s"
	def execute_both():
		cursor.execute(query, (resource_id))
		cursor.execute(query2, (request_id))

	execute_both()
	conn.commit()


def status_reject_request(cursor, conn, request_id):
	query = "UPDATE resource_requests SET request_status = 'Rejected' WHERE request_id = %s"
	cursor.execute(query, (request_id))
	conn.commit()


def report_select_esf_counts(cursor, username):
	query = """
		SELECT A.esf_id, A.description, CASE WHEN B.total_count IS NULL THEN 0 ELSE B.total_count END, CASE WHEN C.used_count IS NULL THEN 0 ELSE C.used_count END FROM esfs A
		LEFT JOIN (SELECT primary_esf_id, COUNT(*) AS total_count FROM resources WHERE owner = %s GROUP BY primary_esf_id) B ON A.esf_id = B.primary_esf_id
			LEFT JOIN (SELECT primary_esf_id, COUNT(*) AS used_count FROM resources WHERE owner = %s AND availability_status = 'In Use' GROUP BY primary_esf_id) C
		ON A.esf_id = C.primary_esf_id ORDER BY A.esf_id ASC
		"""

	cursor.execute(query, (username, username, ))
	query_result = cursor.fetchall()

	return [[esf[0], esf[1], esf[2], esf[3]] for esf in query_result]


def report_select_esf_total(cursor, username):
	query = "SELECT COUNT(*) AS total_count FROM resources WHERE owner = %s"
	cursor.execute(query, (username, ))
	query_result = cursor.fetchall()

	return query_result[0][0]


def report_select_esf_used(cursor, username):
	query = "SELECT COUNT(*) AS used_count FROM resources WHERE owner = %s AND availability_status = 'In Use'"
	cursor.execute(query, (username, ))
	query_result = cursor.fetchall()

	return query_result[0][0]


def incident_add_incident(cursor, conn, abbreviation, owner, incident_date, description, latitude, longitude):
	incident_date = incident_date.split('/')
	incident_date = str(incident_date[2] + '-' + incident_date[0] + '-' + incident_date[1])

	query = """
		INSERT INTO incidents (abbreviation, incident_id, owner, incident_date, description, latitude, longitude)
			SELECT %s, CASE WHEN MAX(incident_id) IS NULL THEN 1 ELSE MAX(incident_id)+1 END, %s, %s, %s, %s, %s FROM incidents where abbreviation = %s
		"""

	cursor.execute(query, (abbreviation, owner, incident_date, description, latitude, longitude, abbreviation))

	query = "SELECT MAX(incident_id) FROM incidents WHERE abbreviation = %s AND owner = %s"
	cursor.execute(query, (abbreviation, owner))
	incident_id = cursor.fetchall()[0][0]

	conn.commit()

	return incident_id