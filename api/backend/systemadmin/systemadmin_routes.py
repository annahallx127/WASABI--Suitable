import logging
from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint for system administration routes
admin = Blueprint('admin', __name__)

#------------------------------------------------------------
# /permissions routes

# Update permissions for existing users or roles
@admin.route('/permissions', methods=['PUT'])
def update_permissions():
    try:
        data = request.json
        user_id = data['user_id']
        access_level = data['access_level']
        description = data['description']
        user_type = data['user_type']
        if user_type == 'Student':
            query = 'UPDATE StudentPermissions SET AccessLevel = %s, AccessDescription = %s WHERE StudentID = %s'
        elif user_type == 'Employer':
            query = 'UPDATE EmployerPermissions SET AccessLevel = %s, AccessDescription = %s WHERE EmployerID = %s'
        elif user_type == 'Admin':
            query = 'UPDATE AdminPermissions SET AccessLevel = %s, AccessDescription = %s WHERE AdminID = %s'
        else:
            return make_response({"error": "Invalid user_type"}, 400)
        cursor = db.get_db().cursor()
        cursor.execute(query, (access_level, description, user_id))
        db.get_db().commit()
        return make_response({"message": "Permissions updated successfully"}, 200)
    except Exception as e:
        return make_response({"error": str(e)}, 500)

# Revoke permissions from a user
@admin.route('/permissions', methods=['DELETE'])
def revoke_permissions():
    try:
        user_id = request.args.get('user_id')
        user_type = request.args.get('user_type')
        if user_type == 'Student':
            query = 'DELETE FROM StudentPermissions WHERE StudentID = %s'
        elif user_type == 'Employer':
            query = 'DELETE FROM EmployerPermissions WHERE EmployerID = %s'
        elif user_type == 'Admin':
            query = 'DELETE FROM AdminPermissions WHERE AdminID = %s'
        else:
            return make_response({"error": "Invalid user_type"}, 400)
        cursor = db.get_db().cursor()
        cursor.execute(query, (user_id,))
        db.get_db().commit()
        return make_response({"message": "Permissions revoked successfully"}, 200)
    except Exception as e:
        return make_response({"error": str(e)}, 500)


# Retrieve current system status
@admin.route('/system-update', methods=['GET'])
def get_system_status():
    query = '''
        SELECT *
        FROM SystemUpdate su
    '''
    cursor = db.get_db().cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return make_response(jsonify(data), 200)

# Submit a report or notification about a system event or issue
@admin.route('/system-update', methods=['POST'])
def submit_system_report():
    try:
        data = request.json
        # Validate input keys
        update_type = data.get('update_type')  # Use .get() to avoid KeyError
        update_date = data.get('update_date')  # Use .get() to allow missing key
        description = data.get('description', 'No description provided')  # Default value

        # Ensure all required fields are provided
        if not update_type or not description:
            return make_response({"error": "update_type and description are required"}, 400)

        # Hardcoding AdminID as 1
        admin_id = 1

        # Use NOW() for update_date if not provided
        if not update_date:
            query = '''
                INSERT INTO SystemUpdate (UpdateType, UpdateDate, Description) 
                VALUES (%s, NOW(), %s)
            '''
            params = (update_type, description)
        else:
            query = '''
                INSERT INTO SystemUpdate (UpdateType, UpdateDate, Description) 
                VALUES (%s, %s, %s)
            '''
            params = (update_type, update_date, description)

        # Execute query
        cursor = db.get_db().cursor()
        cursor.execute(query, params)
        db.get_db().commit()

        return make_response("System event submitted successfully", 200)
    except KeyError as e:
        current_app.logger.error(f"Missing key in request: {str(e)}")
        return make_response({"error": f"Missing key: {str(e)}"}, 400)
    except Exception as e:
        current_app.logger.error(f"Error submitting system report: {str(e)}")
        return make_response({"error": str(e)}, 500)



# Update system health monitoring configurations or thresholds
@admin.route('/system-update', methods=['PUT'])
def update_health_config():
    data = request.json
    update_id = data['update_id']
    description = data['description']
    query = 'UPDATE SystemUpdate SET Description = %s WHERE UpdateID = %s'
    cursor = db.get_db().cursor()
    cursor.execute(query, (description, update_id))
    db.get_db().commit()
    return make_response("System monitoring configuration updated", 200)

# Clear outdated or irrelevant system logs
@admin.route('/system-update/logs', methods=['DELETE'])
def clear_logs():
    query = 'DELETE FROM DataArchive WHERE ArchiveDate < NOW() - INTERVAL 127 DAY'
    cursor = db.get_db().cursor()
    cursor.execute(query)
    db.get_db().commit()
    return make_response("Outdated logs cleared", 200)

#------------------------------------------------------------
# /alert-system routes

# Retrieve audit logs of user actions and system changes
@admin.route('/alert-system/audit-logs', methods=['GET'])
def get_audit_logs():
    try:
        query = '''
            SELECT a.AlertID, a.ActivityType, a.Description, a.Severity, a.Timestamp, a.Status,
                   CASE 
                       WHEN a.GeneratedByStudent IS NOT NULL THEN 'Student'
                       WHEN a.GeneratedByEmployer IS NOT NULL THEN 'Employer'
                       WHEN a.GeneratedByAdmin IS NOT NULL THEN 'Admin'
                   END AS GeneratedByType
            FROM AlertSystem a
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        return make_response(jsonify(data), 200)
    except Exception as e:
        return make_response({"error": str(e)}, 500)

# Submit new alerts or event flags
@admin.route('/alert-system', methods=['POST'])
def submit_alert():
    data = request.json
    activity_type = data['activity_type']
    description = data['description']
    severity = data['severity']
    generated_by = data['generated_by']
    query = 'INSERT INTO AlertSystem (ActivityType, Description, Severity, Timestamp, GeneratedByStudent) VALUES (%s, %s, %s, NOW(), %s)'
    cursor = db.get_db().cursor()
    cursor.execute(query, (activity_type, description, severity, generated_by))
    db.get_db().commit()
    return make_response("Alert submitted successfully", 200)

# Update alert configurations or mark specific alerts as resolved
@admin.route('/alert-system', methods=['PUT'])
def update_alert_config():
    data = request.json
    alert_id = data['alert_id']
    status = data['status']
    query = 'UPDATE AlertSystem SET Status = %s WHERE AlertID = %s'
    cursor = db.get_db().cursor()
    cursor.execute(query, (status, alert_id))
    db.get_db().commit()
    return make_response("Alert updated successfully", 200)

# Delete logs older than the retention policy
@admin.route('/alert-system/logs', methods=['DELETE'])
def delete_old_logs():
    query = 'DELETE FROM AlertSystem WHERE Timestamp < NOW() - INTERVAL 30 DAY'
    cursor = db.get_db().cursor()
    cursor.execute(query)
    db.get_db().commit()
    return make_response("Old logs deleted", 200)

#------------------------------------------------------------
# /job-listings routes

#------------------------------------------------------------

#Get All Active Jobs
@admin.route('/job-listings/active', methods=['GET'])
def get_active_job_listings():
    current_app.logger.info('GET /job-listings/active route')

    cursor = db.get_db().cursor()
    cursor.execute("""
        SELECT JobListingID
        FROM JobListings
        WHERE JobIsActive = True
    """)

    active_jobs = cursor.fetchall()

    # Check if there are any expired job listings
    if active_jobs:
        the_response = make_response(jsonify(active_jobs))
        the_response.status_code = 200
        return the_response
    else:
        return jsonify({'message': 'No active job listings found'}), 404


# Get all expired job listings
@admin.route('/job-listings/expired', methods=['GET'])
def get_expired_job_listings():
    current_app.logger.info('GET /job-listings/expired route')

    # Query to fetch job listings where the expiration date (JobIsActive) is less than the current time
    cursor = db.get_db().cursor()
    cursor.execute("""
        SELECT *
        FROM JobListings
        WHERE JobIsActive = False
    """)

    expired_jobs = cursor.fetchall()

    # Check if there are any expired job listings
    if expired_jobs:
        the_response = make_response(jsonify(expired_jobs))
        the_response.status_code = 200
        return the_response
    else:
        return jsonify({'message': 'No expired job listings found'}), 404

# Retrieve detailed information about a specific job posting
@admin.route('/job-listings/<id>', methods=['GET'])
def get_job_details(id):
    query = '''
        SELECT jl.JobListingID, jl.JobPositionTitle, jl.JobDescription, jl.JobIsActive, 
               c.Name AS CompanyName, c.Industry,
               hm.FirstName AS HiringManagerFirstName, hm.LastName AS HiringManagerLastName
        FROM JobListings jl
        JOIN Company c ON jl.CompanyID = c.CompanyID
        JOIN HiringManager hm ON c.EmployerID = hm.EmployerID
        WHERE jl.JobListingID = %s
    '''
    cursor = db.get_db().cursor()
    cursor.execute(query, (id,))
    data = cursor.fetchall()
    return make_response(jsonify(data), 200)

# Delete a job listing
@admin.route('/job-listings/<id>', methods=['DELETE'])
def delete_job_listing(id):
    query = 'DELETE FROM JobListings WHERE JobListingID = %s'
    cursor = db.get_db().cursor()
    cursor.execute(query, (id,))
    db.get_db().commit()
    return make_response("Job listing deleted successfully", 200)

#Get users
@admin.route('/users', methods=['GET'])
def get_users():
    try:
        user_type = request.args.get('type')
        current_app.logger.info(f"Fetching users with type: {user_type}")
        
        if user_type == 'Student':
            query = 'SELECT StudentID, FirstName, LastName, Major, isMentor, WCFI FROM Student'
        elif user_type == 'Employer':
            query = 'SELECT EmployerID, FirstName, LastName, Position FROM HiringManager'
        elif user_type == 'Admin':
            query = 'SELECT AdminID, FirstName, LastName FROM SystemsAdministrator'
        else:
            query = '''
                SELECT 'Student' AS UserType, StudentID AS ID, FirstName, LastName FROM Student
                UNION ALL
                SELECT 'Employer', EmployerID, FirstName, LastName FROM HiringManager
                UNION ALL
                SELECT 'Admin', AdminID, FirstName, LastName FROM SystemsAdministrator
            '''
        cursor = db.get_db().cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        current_app.logger.info(f"Fetched users: {data}")
        return make_response(jsonify(data), 200)
    except Exception as e:
        current_app.logger.error(f"Error fetching users: {str(e)}")
        return make_response({"error": str(e)}, 500)


# Delete a user account
@admin.route('/users', methods=['DELETE'])
def delete_user():
    user_id = request.args.get('id')
    user_type = request.args.get('user_type')
    if user_type == 'Student':
        query = 'DELETE FROM Student WHERE StudentID = %s'
    elif user_type == 'Employer':
        query = 'DELETE FROM HiringManager WHERE EmployerID = %s'
    elif user_type == 'Admin':
        query = 'DELETE FROM SystemsAdministrator WHERE AdminID = %s'
    else:
        return make_response("Invalid user type", 400)

    cursor = db.get_db().cursor()
    cursor.execute(query, (user_id,))
    db.get_db().commit()
    return make_response("User deleted successfully", 200)
