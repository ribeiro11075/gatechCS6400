from flask import Flask, render_template, session, redirect, request, url_for, flash
from flaskext.mysql import MySQL
from data import *
import unicodedata
import datetime

app = Flask(__name__)
app.secret_key = 'cs6400'

#----------------------------------------------------
# There are 2 DB Connection alternatives
# Comment and uncomment below based on the situation
#----------------------------------------------------
"""
# Option 1 - use your localhost
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'cs6400'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cs6400'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_DB'] = 'cs6400'
mysql.init_app(app)

"""
#Option 2 - use online server

app.config['MYSQL_DATABASE_HOST'] = 'sql9.freemysqlhosting.net'
app.config['MYSQL_DATABASE_USER'] = 'sql9246305'
app.config['MYSQL_DATABASE_PASSWORD'] = 'vschi4TZMF'
app.config['MYSQL_DATABASE_DB'] = 'sql9246305'
mysql = MySQL(app)


def check_session(session):
    if session.get('logged_in') is None:
        session['logged_in'] = False

    if session['logged_in'] == False:
        return False
    else:
        return True


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
        return False


def is_date(d):
    try:
        datetime.datetime.strptime(d, '%m/%d/%Y')
        return True
    except ValueError:
        return False


# Jinja2 template filter to convert date.time into format we want in string
@app.template_filter('format_date')
def format_date(d):
    if isinstance(d, str):
        if d == "NOW":
            return "NOW"
        else:
            d = datetime.datetime.strptime(d, "%Y-%m-%d")
    return datetime.datetime.strftime(d, "%m/%d/%Y")


# Jinja2 filter to format distance
@app.template_filter('format_distance')
def format_distance(n):
    if n is None or n == "":
        return ""

    if isinstance(n,str):
        n = int(n)

    return "{:,}".format(round(float(n),1)) + " km"


# Jinja2 filter to format cost
@app.template_filter('format_cost')
def format_cost(c):
    return "$"+"{:,}".format(int(round(c)))


@app.route('/')
def home():
    if not check_session(session):
        return redirect(url_for('login'))

    conn = mysql.connect()
    cursor = conn.cursor()
    user_details = menu_select_user_details(cursor, session['username'])

    return render_template('menu.html', user_details = user_details)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    error = None

    if not check_session(session):
        if request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor()

            password = login_select_users(cursor, request.form['inputUsername'])
            conn.close()

            if password is None:
                error = 'Invalid Credentials'
            elif password != request.form['inputPassword']:
                error = 'Invalid Password'
            else:
                session['logged_in'] = True
                session['username'] = request.form['inputUsername']
                flash('You are now logged in', 'success')
                return redirect(url_for('menu'))
    else:
        return redirect(url_for('menu'))

    return render_template('login.html', error = error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return home()


@app.route('/menu')
def menu():
    if not check_session(session):
        return redirect(url_for('login'))

    conn = mysql.connect()
    cursor = conn.cursor()
    user_details = menu_select_user_details(cursor, session['username'])

    return render_template('menu.html', user_details=user_details)


@app.route('/resource', methods = ['GET', 'POST'])
def resource():
    if not check_session(session):
        return redirect(url_for('login'))

    error = list()

    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()

        owner = session['username']
        resource_name = request.form['inputResourceName']
        latitude = request.form['inputLat']
        longitude = request.form['inputLon']
        model = request.form['inputModel']
        cost = request.form['inputCost']
        cost_per = request.form['inputPer']
        max_distance = request.form['inputMaxDistance']
        primary_esf_id = request.form['inputPrimaryESF']
        capabilities = request.form.getlist('inputCapabilities')
        secondary_esfs = request.form.getlist('inputSecondaryESFs')
        if max_distance == '':
            max_distance = 25000

        if len(error) == 0:
            resource_id = resource_add_resource(cursor, conn, owner, resource_name, latitude, longitude, model, cost, cost_per, max_distance, primary_esf_id)

            for capability in capabilities:
                resource_add_capabilities(cursor, conn, resource_id, capability)

            for secondary_esf_id in secondary_esfs:
                resource_add_secondary_esfs(cursor, conn, resource_id, secondary_esf_id)

            flash('You have successfully added resource %s' % resource_name, 'success')
            return redirect(url_for('menu'))

        conn.close()

    conn = mysql.connect()
    cursor = conn.cursor()

    cost_pers = resource_select_cost_pers(cursor)
    esfs = resource_select_esfs(cursor)

    conn.close()

    return render_template('resource.html', cost_pers = cost_pers, esfs = esfs, error = error)


@app.route('/incident', methods = ['GET', 'POST'])
def incident():
    if not check_session(session):
        return redirect(url_for('login'))

    error = list()

    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()

        abbreviation = request.form['inputDeclaration']
        owner = session['username']
        incident_date = request.form['incidentDate']
        description = request.form['inputDescription']
        latitude = request.form['inputLat']
        longitude = request.form['inputLon']

        if len(error) == 0:
            incident_id = incident_add_incident(cursor, conn, abbreviation, owner, incident_date, description, latitude, longitude)
            flash('You have successfully added incident %s-%s' % (abbreviation, incident_id), 'success')
            return redirect(url_for('menu'))

        conn.close()

    conn = mysql.connect()
    cursor = conn.cursor()

    incident_types = incident_select_incident_types(cursor)

    conn.close()

    return render_template('incident.html', incident_types = incident_types, error = error)


@app.route('/search')
def search():
    if not check_session(session):
        return redirect(url_for('login'))

    conn = mysql.connect()
    cursor = conn.cursor()

    esfs = search_select_esfs(cursor)
    incidents = search_select_incidents(cursor, session['username'])

    conn.close()

    return render_template('search.html', esfs = esfs, incidents = incidents)


def refresh_results(cursor, search_params):
    results_tbl = results_select_resources(cursor, session['username'], search_params[0], search_params[1], search_params[2], search_params[3], search_params[4], search_params[5])
    #for the search page
    #--------------------
    esfs = search_select_esfs(cursor)
    incidents = search_select_incidents(cursor, session['username'])
    return (results_tbl, esfs, incidents)


@app.route('/search/results', methods=["GET", "POST"])
def results():
    global search_params
    if not check_session(session):
        return redirect(url_for('login'))
    # for the results page
    #--------------------
    if request.method == "POST":
        keyword = request.form["inputKeyword"]
        esf_id = request.form["inputESF"]
        try:
            incident_id = request.form["inputIncident"].split(':')[0].split('-')[1]
            abbreviation = request.form["inputIncident"].split(':')[0].split('-')[0]
            description = request.form["inputIncident"].split(':')[1]
        except:
            incident_id = ""
            abbreviation = ""
            description =""
        location = request.form["inputLocation"]

    conn = mysql.connect()
    cursor = conn.cursor()
    # Conditional select based on parameters
    criteria = "none"
    if location:
        if not incident_id:
            criteria = "invalid"
            flash("Please select an incident from which the radius distance will be calculated", 'danger')
            keyword = '%'+keyword+'%'
        else :
            if keyword and esf_id:
                criteria="loc-key-esf-inc"
                keyword = '%'+keyword+'%'
            elif keyword:
                criteria="loc-key-inc"
                keyword = '%'+keyword+'%'
            elif esf_id:
                criteria="loc-esf-inc"
            else:
                criteria="inc"
                keyword = '%'+keyword+'%'
    else:
        if not location and incident_id and esf_id:
            criteria = "loc-key-esf-inc"
            keyword = '%'+keyword+'%'
            location = 25000
        elif keyword and esf_id:
            criteria = "noloc-key-esf"
            keyword = '%'+keyword+'%'
        elif keyword:
            criteria="noloc-key"
            keyword = '%'+keyword+'%'
        elif esf_id:
            criteria="noloc-esf"
            keyword = '%'+keyword+'%'
        elif incident_id:
            criteria="inc"
            location = 25000
        else:
            criteria = "none"

    search_params = [keyword, esf_id, incident_id, abbreviation, location, criteria, description]
    esfs = search_select_esfs(cursor)
    incidents = search_select_incidents(cursor, session['username'])
    results_tbl = results_select_resources(cursor, session['username'], search_params[0], search_params[1], search_params[2], search_params[3], search_params[4], search_params[5])

    conn.close()

    return render_template('results.html', results_tbl = results_tbl, search_params=search_params, esfs = esfs, incidents = incidents)


@app.route('/search/request', methods=["GET", "POST"])
def search_results_request() :
    if request.method == "POST"  and request.form["incident_id"]:
        resource_id = int(request.form["resource_id"])
        abbreviation = str(request.form["abbreviation"])
        incident_id = int(request.form["incident_id"])
        requested_start_date = str(request.form["requested_start_date"])
        expected_return_date = str(request.form["expected_return_date"])

        conn = mysql.connect()
        cursor = conn.cursor()
        results_request_resource(cursor, conn, resource_id, abbreviation, incident_id, requested_start_date, expected_return_date)
        conn.close()
        flash("Request sent successfully!", 'success')
    else:
        flash("Sorry, request attempt failed. Please makes sure your search query includes an incident.",'danger')

    conn = mysql.connect()
    cursor = conn.cursor()
    results_tbl, esfs, incidents = refresh_results(cursor, search_params)
    conn.commit()

    return render_template('results.html', results_tbl = results_tbl, search_params=search_params, esfs = esfs, incidents = incidents)


@app.route('/search/deploy', methods=["GET", "POST"])
def search_results_deploy():
    if request.method == "POST" and request.form["owner"]== session["username"] and request.form["incident_id"]:
        resource_id = int(request.form["resource_id"])
        abbreviation = str(request.form["abbreviation"])
        incident_id = int(request.form["incident_id"])
        expected_return_date = str(request.form["expected_return_date"])

        conn = mysql.connect()
        cursor = conn.cursor()
        results_deploy_resource(cursor, conn, resource_id, abbreviation, incident_id, expected_return_date)
        conn.close()
        flash("Resouce susccessfully Deployed!", 'success')
    else:
        flash("Unable to deploy resource. Please select an incident that you own in the search parameters.",'danger')

    conn = mysql.connect()
    cursor = conn.cursor()
    results_tbl, esfs, incidents = refresh_results(cursor, search_params)
    conn.close()

    return render_template('results.html', results_tbl = results_tbl, search_params=search_params, esfs = esfs, incidents = incidents)


def refresh_status(cursor):
    inuse = status_select_inuse(cursor, session['username'])
    myrequests = status_select_myrequests(cursor, session['username'])
    myresponses = status_select_myresponses(cursor, session['username'])

    return (inuse, myrequests, myresponses)


@app.route('/status')
def status():
    if not check_session(session):
        return redirect(url_for('login'))

    # populate all 3 sections
    conn = mysql.connect()
    cursor = conn.cursor()
    output = refresh_status(cursor)
    conn.close()

    return render_template('status.html' , inuse=output[0], myrequests=output[1], myresponses=output[2])


@app.route('/status/return', methods=["GET", "POST"])
def status_return():
    if request.method=="POST":
        request_id = request.form["request_id"]
        resource_id = request.form["resource_id"]

        conn =mysql.connect()
        cursor=conn.cursor()
        status_return_resource(cursor, conn, request_id, resource_id)
        conn.close()

    conn =mysql.connect()
    cursor=conn.cursor()
    output = refresh_status(cursor)
    conn.close()
    flash("Resource #" +str(resource_id) +" successfully returned!", "success")

    return render_template('status.html' , inuse=output[0], myrequests=output[1], myresponses=output[2])


@app.route('/status/cancel', methods=["GET", "POST"])
def status_cancel():
    if request.method=="POST":
        request_id = request.form["request_id"]

        conn =mysql.connect()
        cursor=conn.cursor()
        status_cancel_request(cursor, conn, request_id)
        conn.close()

    conn =mysql.connect()
    cursor=conn.cursor()
    output = refresh_status(cursor)
    conn.close()
    flash("Request #" +str(request_id) +" successfully cancelled!", "success")

    return render_template('status.html' , inuse=output[0], myrequests=output[1], myresponses=output[2])


@app.route('/status/deploy', methods=["GET", "POST"])
def status_deploy():
    if request.method == "POST":
        request_id = request.form["request_id"]
        resource_id = request.form["resource_id"]
        expected_return_date = request.form["expected_return_date"]

        conn = mysql.connect()
        cursor = conn.cursor()

        chk = status_check_availability(cursor, resource_id)
        if  chk > 0:
            conn.close()
            flash("Resource #" + str(resource_id) +" is already deployed. Please wait until its available", 'danger')
        else:
            status_deploy_resource(cursor, conn, request_id, resource_id, expected_return_date)
            conn.close()
            flash("Resource #" + str(resource_id) + " successfully deployed!", "success")

    conn =mysql.connect()
    cursor=conn.cursor()
    output = refresh_status(cursor)
    conn.close()

    return render_template('status.html' , inuse=output[0], myrequests=output[1], myresponses=output[2])


@app.route('/status/reject', methods=["GET", "POST"])
def status_reject():
    if request.method == "POST":
        request_id = request.form["request_id"]

        conn = mysql.connect()
        cursor = conn.cursor()
        status_reject_request(cursor, conn, request_id)
        conn.close()

    conn = mysql.connect()
    cursor = conn.cursor()
    output = refresh_status(cursor)
    conn.close()

    flash("Request #" + str(request_id) + " has been successfully rejected.", 'success')
    return render_template('status.html' , inuse=output[0], myrequests=output[1], myresponses=output[2])


@app.route('/report')
def report():
    if not check_session(session):
        return redirect(url_for('login'))

    conn = mysql.connect()
    cursor = conn.cursor()

    esf_counts = report_select_esf_counts(cursor, session['username'])
    total_count = report_select_esf_total(cursor, session['username'])
    used_count = report_select_esf_used(cursor, session['username'])
    conn.close()

    return render_template('report.html', esf_counts = esf_counts, total_count = total_count, used_count = used_count)


if __name__ == '__main__':
    app.debug = True
    app.run()
