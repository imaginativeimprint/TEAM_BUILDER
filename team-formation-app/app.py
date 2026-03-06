from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from database import init_db, get_db
import csv
import os
import sqlite3
from datetime import datetime
import socket

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize database
init_db()

# Load student data from CSV
def load_students():
    students = {}
    csv_path = os.path.join('data', 'students.csv')
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found. Creating empty students dictionary.")
            return students
            
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                if len(row) >= 2:
                    usn = row[0].strip().upper()
                    name = row[1].strip()
                    # Extract last 3 digits
                    last_three = usn[-3:] if len(usn) >= 3 else usn
                    students[last_three] = {
                        'full_usn': usn,
                        'name': name,
                        'last_three': last_three
                    }
        print(f"Loaded {len(students)} students successfully")
    except Exception as e:
        print(f"Error loading students: {e}")
    return students

STUDENTS = load_students()

# Function to rebuild CSV from database (ensures perfect ordering)
def rebuild_csv_from_db():
    csv_path = os.path.join('data', 'CSE3_DBMS_team_details.csv')
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get all team members in order of team creation
        cursor.execute("""
            SELECT tm.usn, tm.name, t.created_at 
            FROM team_members tm 
            JOIN teams t ON tm.team_id = t.id 
            ORDER BY t.created_at ASC, tm.id ASC
        """)
        
        all_members = cursor.fetchall()
        
        # Write to CSV with sequential numbers
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Sl No.', 'USN', 'Name'])
            
            for idx, member in enumerate(all_members, start=1):
                writer.writerow([idx, member[0], member[1]])
        
        return True
    except Exception as e:
        print(f"Error rebuilding CSV: {e}")
        return False
    finally:
        db.close()

# Save team details to CSV with proper sequential numbering
def save_to_csv(team_data):
    csv_path = os.path.join('data', 'CSE3_DBMS_team_details.csv')
    
    try:
        # First, read existing data to get the last Sl No.
        existing_rows = []
        if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)  # Read headers
                for row in csv_reader:
                    if row:
                        existing_rows.append(row)
        
        # Next Sl No. is after all existing rows
        next_sl_no = len(existing_rows) + 1
        
        # Append new members
        with open(csv_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header if file doesn't exist
            if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
                writer.writerow(['Sl No.', 'USN', 'Name'])
            
            # Write each member with sequential Sl No.
            for member in team_data['members']:
                writer.writerow([
                    next_sl_no,
                    member['usn'],
                    member['name']
                ])
                next_sl_no += 1
        
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False

# Check if student is already in any team
def check_student_in_teams(usn, exclude_team_id=None):
    db = get_db()
    cursor = db.cursor()
    
    try:
        if exclude_team_id:
            cursor.execute("""
                SELECT t.team_name, t.team_number 
                FROM teams t 
                JOIN team_members tm ON t.id = tm.team_id 
                WHERE tm.usn = ? AND t.id != ?
            """, (usn, exclude_team_id))
        else:
            cursor.execute("""
                SELECT t.team_name, t.team_number 
                FROM teams t 
                JOIN team_members tm ON t.id = tm.team_id 
                WHERE tm.usn = ?
            """, (usn,))
        
        result = cursor.fetchone()
        if result:
            return {
                'in_team': True,
                'team_name': result[0],
                'team_number': result[1]
            }
        return {'in_team': False}
    except Exception as e:
        print(f"Error checking student: {e}")
        return {'in_team': False}
    finally:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-team')
def create_team():
    return render_template('create_team.html')

@app.route('/api/get-student/<last_three>')
def get_student(last_three):
    student = STUDENTS.get(last_three.upper())
    
    if student:
        # Check if student is already in any team
        team_check = check_student_in_teams(student['full_usn'])
        
        if team_check['in_team']:
            return jsonify({
                'success': False,
                'message': f'Student is already in team {team_check["team_name"]} ({team_check["team_number"]})'
            })
        
        return jsonify({
            'success': True,
            'usn': student['full_usn'],
            'name': student['name']
        })
    
    return jsonify({'success': False, 'message': 'Student not found in database'})

@app.route('/api/save-team', methods=['POST'])
def save_team():
    data = request.json
    team_name = data.get('team_name')
    secret_key = data.get('secret_key')
    members = data.get('members')
    
    # Validate team has 3-4 members
    if len(members) < 3 or len(members) > 4:
        return jsonify({'success': False, 'message': 'Team must have 3-4 members'})
    
    # Check for duplicate USNs
    usns = [m['usn'] for m in members]
    if len(usns) != len(set(usns)):
        return jsonify({'success': False, 'message': 'Duplicate members not allowed'})
    
    # Check if any member is already in another team
    for member in members:
        team_check = check_student_in_teams(member['usn'])
        if team_check['in_team']:
            return jsonify({
                'success': False, 
                'message': f"{member['name']} is already in team {team_check['team_name']} ({team_check['team_number']})"
            })
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get next team number
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        team_number = f"TEAM{team_count + 1}"
        
        # Insert team
        cursor.execute(
            "INSERT INTO teams (team_name, team_number, secret_key, created_at) VALUES (?, ?, ?, ?)",
            (team_name, team_number, secret_key, datetime.now())
        )
        team_id = cursor.lastrowid
        
        # Insert members
        for member in members:
            cursor.execute(
                "INSERT INTO team_members (team_id, usn, name, last_three) VALUES (?, ?, ?, ?)",
                (team_id, member['usn'], member['name'], member['last_three'])
            )
        
        db.commit()
        
        # Save to CSV file
        csv_data = {
            'members': members
        }
        save_to_csv(csv_data)
        
        return jsonify({
            'success': True,
            'message': 'Team created successfully',
            'team_number': team_number
        })
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@app.route('/api/get-teams')
def get_teams():
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT t.*, GROUP_CONCAT(tm.name || ' (' || tm.usn || ')') as members_list 
            FROM teams t 
            LEFT JOIN team_members tm ON t.id = tm.team_id 
            GROUP BY t.id
            ORDER BY t.created_at DESC
        """)
        
        teams = cursor.fetchall()
        
        teams_list = []
        for team in teams:
            teams_list.append({
                'id': team[0],
                'team_name': team[1],
                'team_number': team[2],
                'created_at': team[4],
                'members': team[5].split(',') if team[5] else []
            })
        
        return jsonify({'success': True, 'teams': teams_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@app.route('/edit-team/<team_number>')
def edit_team(team_number):
    return render_template('edit_team.html', team_number=team_number)

@app.route('/admin-edit-team/<team_number>')
def admin_edit_team(team_number):
    # Admin edit - bypasses secret key
    return render_template('edit_team.html', team_number=team_number, admin_mode=True)

@app.route('/api/get-team/<team_number>')
def get_team(team_number):
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT * FROM teams WHERE team_number = ?", (team_number,))
        team = cursor.fetchone()
        
        if not team:
            return jsonify({'success': False, 'message': 'Team not found'})
        
        cursor.execute("SELECT usn, name, last_three FROM team_members WHERE team_id = ?", (team[0],))
        members = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'team': {
                'id': team[0],
                'team_name': team[1],
                'team_number': team[2],
                'secret_key': team[3],
                'created_at': team[4]
            },
            'members': [{'usn': m[0], 'name': m[1], 'last_three': m[2]} for m in members]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@app.route('/api/update-team', methods=['POST'])
def update_team():
    data = request.json
    team_number = data.get('team_number')
    secret_key = data.get('secret_key')
    new_secret_key = data.get('new_secret_key')
    members = data.get('members')
    admin_mode = data.get('admin_mode', False)
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get team details
        cursor.execute("SELECT id, secret_key, team_name FROM teams WHERE team_number = ?", (team_number,))
        team = cursor.fetchone()
        
        if not team:
            return jsonify({'success': False, 'message': 'Team not found'})
        
        # Verify secret key only if not in admin mode
        if not admin_mode and team[1] != secret_key:
            return jsonify({'success': False, 'message': 'Invalid secret key'})
        
        # Get old members for history
        cursor.execute("SELECT usn FROM team_members WHERE team_id = ?", (team[0],))
        old_usns = [m[0] for m in cursor.fetchall()]
        
        # Validate members
        if len(members) < 3 or len(members) > 4:
            return jsonify({'success': False, 'message': 'Team must have 3-4 members'})
        
        usns = [m['usn'] for m in members]
        if len(usns) != len(set(usns)):
            return jsonify({'success': False, 'message': 'Duplicate members not allowed'})
        
        # Check if any new member is already in another team
        for member in members:
            if member['usn'] not in old_usns:
                team_check = check_student_in_teams(member['usn'], team[0])
                if team_check['in_team']:
                    return jsonify({
                        'success': False,
                        'message': f"{member['name']} is already in team {team_check['team_name']} ({team_check['team_number']})"
                    })
        
        # Update secret key if provided
        if new_secret_key and new_secret_key != secret_key:
            cursor.execute("UPDATE teams SET secret_key = ? WHERE id = ?", (new_secret_key, team[0]))
        
        # Delete old members
        cursor.execute("DELETE FROM team_members WHERE team_id = ?", (team[0],))
        
        # Insert new members
        for member in members:
            cursor.execute(
                "INSERT INTO team_members (team_id, usn, name, last_three) VALUES (?, ?, ?, ?)",
                (team[0], member['usn'], member['name'], member['last_three'])
            )
        
        db.commit()
        
        # Rebuild entire CSV to ensure correct ordering
        rebuild_csv_from_db()
        
        return jsonify({'success': True, 'message': 'Team updated successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

# Admin delete route with CSV cleanup
@app.route('/api/admin/delete-team/<int:team_id>', methods=['DELETE'])
def admin_delete_team(team_id):
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Delete team members
        cursor.execute("DELETE FROM team_members WHERE team_id = ?", (team_id,))
        
        # Delete the team
        cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        
        db.commit()
        
        # Rebuild entire CSV from database to ensure perfect ordering
        rebuild_csv_from_db()
        
        return jsonify({
            'success': True,
            'message': 'Team deleted successfully and CSV reorganized'
        })
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        })
    finally:
        db.close()

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/project-submission')
def project_submission():
    return render_template('project_submission.html')

@app.route('/api/verify-team-for-submission', methods=['POST'])
def verify_team_for_submission():
    data = request.json
    team_number = data.get('team_number')
    secret_key = data.get('secret_key')
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT id, team_name, secret_key FROM teams WHERE team_number = ?", (team_number,))
        team = cursor.fetchone()
        
        if not team:
            return jsonify({'success': False, 'message': 'Team not found'})
        
        if team[2] != secret_key:
            return jsonify({'success': False, 'message': 'Invalid secret key'})
        
        # Get team members for display
        cursor.execute("SELECT name, usn FROM team_members WHERE team_id = ?", (team[0],))
        members = cursor.fetchall()
        
        member_list = [{'name': m[0], 'usn': m[1]} for m in members]
        
        return jsonify({
            'success': True,
            'team_name': team[1],
            'members': member_list
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@app.route('/view-csv')
def view_csv():
    csv_path = os.path.join('data', 'CSE3_DBMS_team_details.csv')
    
    # Get teams from database to know actual team groupings
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get all teams with their members in order
        cursor.execute("""
            SELECT t.id, t.team_number, t.team_name, t.created_at,
                   tm.usn, tm.name
            FROM teams t
            LEFT JOIN team_members tm ON t.id = tm.team_id
            ORDER BY t.created_at ASC, tm.id ASC
        """)
        
        rows = cursor.fetchall()
        
        # Group by team
        teams_data = {}
        for row in rows:
            team_id = row[0]
            if team_id not in teams_data:
                teams_data[team_id] = {
                    'team_number': row[1],
                    'team_name': row[2],
                    'created_at': row[3],
                    'members': []
                }
            if row[4]:  # If there's a member (USN)
                teams_data[team_id]['members'].append({
                    'usn': row[4],
                    'name': row[5]
                })
        
        # Also read CSV for Sl No. display
        csv_members = []
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip header
                for row in csv_reader:
                    if row:
                        csv_members.append({
                            'sl_no': row[0],
                            'usn': row[1],
                            'name': row[2]
                        })
        
        # Generate HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CSE DBMS Team Details</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    background: url('https://images.pexels.com/photos/163064/play-stone-network-networked-interactive-163064.jpeg') no-repeat center center fixed;
                    padding: 20px; 
                }
                .container { 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    background: rgba(255,255,255,0.95);
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }
                h1 { 
                    color: #667eea; 
                    text-align: center;
                    margin-bottom: 10px;
                    font-size: 2.5em;
                }
                .subtitle {
                    text-align: center;
                    color: #666;
                    margin-bottom: 30px;
                }
                .team-section { 
                    background: white; 
                    border-radius: 15px; 
                    padding: 25px; 
                    margin-bottom: 30px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                    border-left: 5px solid #667eea;
                    transition: transform 0.3s;
                }
                .team-section:hover {
                    transform: translateX(5px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                }
                .team-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 2px solid #f0f0f0;
                }
                .team-title h2 {
                    color: #333;
                    font-size: 1.5em;
                    margin-bottom: 5px;
                }
                .team-title .team-number {
                    color: #667eea;
                    font-weight: bold;
                    font-size: 1.1em;
                }
                .team-badge {
                    background: #28a745;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.9em;
                }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 15px;
                    border-radius: 10px;
                    overflow: hidden;
                }
                th { 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; 
                    padding: 12px; 
                    text-align: left; 
                    font-weight: 600;
                }
                td { 
                    padding: 10px; 
                    border: 1px solid #e0e0e0; 
                }
                tr:nth-child(even) { background: #f8f9fa; }
                tr:hover { background: #e8f4fd; }
                .stats-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .stat-box {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    border-left: 5px solid #667eea;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .stat-box .number {
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }
                .back-btn { 
                    display: inline-block; 
                    margin-top: 30px; 
                    padding: 12px 30px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; 
                    text-decoration: none; 
                    border-radius: 25px;
                    transition: all 0.3s;
                }
                .back-btn:hover {
                    transform: scale(1.05);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }
                .button-group {
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 20px;
                }
                .btn {
                    padding: 10px 25px;
                    border: none;
                    border-radius: 25px;
                    cursor: pointer;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s;
                }
                .btn-success {
                    background: #28a745;
                    color: white;
                }
                .btn-success:hover {
                    background: #218838;
                    transform: scale(1.05);
                }
                @media (max-width: 768px) {
                    .team-header {
                        flex-direction: column;
                        gap: 10px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 CSE DBMS Team Details</h1>
                <p class="subtitle">Teams grouped by Team ID with proper member listing</p>
        """
        
        if teams_data:
            # Stats
            total_teams = len(teams_data)
            total_members = sum(len(team['members']) for team in teams_data.values())
            avg_size = round(total_members / total_teams, 1) if total_teams > 0 else 0
            
            html += f"""
            <div class="stats-container">
                <div class="stat-box">
                    <div class="number">{total_teams}</div>
                    <div class="label">Total Teams</div>
                </div>
                <div class="stat-box">
                    <div class="number">{total_members}</div>
                    <div class="label">Total Members</div>
                </div>
                <div class="stat-box">
                    <div class="number">{avg_size}</div>
                    <div class="label">Avg Team Size</div>
                </div>
            </div>
            """
            
            # Display each team
            for team_id, team in teams_data.items():
                # Find corresponding Sl Nos from CSV
                team_members_with_sl = []
                for member in team['members']:
                    # Find matching Sl No from CSV
                    sl_no = next((item['sl_no'] for item in csv_members if item['usn'] == member['usn']), 'N/A')
                    team_members_with_sl.append({
                        'sl_no': sl_no,
                        'usn': member['usn'],
                        'name': member['name']
                    })
                
                # Format created_at date
                created_date = ''
                if team['created_at']:
                    try:
                        if isinstance(team['created_at'], str):
                            created_date = datetime.fromisoformat(team['created_at']).strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            created_date = team['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        created_date = str(team['created_at'])
                
                html += f"""
                <div class="team-section">
                    <div class="team-header">
                        <div class="team-title">
                            <h2>{team['team_name']}</h2>
                            <span class="team-number">{team['team_number']}</span>
                        </div>
                        <span class="team-badge">Team ID: {team_id}</span>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Sl No.</th>
                                <th>USN</th>
                                <th>Name</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                for member in team_members_with_sl:
                    html += f"""
                    <tr>
                        <td>{member['sl_no']}</td>
                        <td>{member['usn']}</td>
                        <td>{member['name']}</td>
                    </tr>
                    """
                
                html += f"""
                        </tbody>
                    </table>
                    <p style="text-align: right; margin-top: 10px; color: #666; font-size: 0.9em;">
                        Created: {created_date}
                    </p>
                </div>
                """
            
            html += """
            <div class="button-group">
                <a href="/download-csv" class="btn btn-success">📥 Download CSV</a>
                <a href="/admin" class="back-btn">← Back to Admin</a>
            </div>
            """
        else:
            html += """
            <div style="text-align: center; padding: 50px; color: #999;">
                <div style="font-size: 4em;">📭</div>
                <h3>No Teams Found</h3>
                <p>Create some teams to see them here!</p>
                <a href="/admin" class="back-btn" style="margin-top: 20px;">← Back to Admin</a>
            </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        db.close()
@app.route('/download-csv')
def download_csv():
    csv_path = os.path.join('data', 'CSE3_DBMS_team_details.csv')
    
    if os.path.exists(csv_path):
        # Create a temporary file with proper formatting
        import tempfile
        import shutil
        
        # Create a temp file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8')
        
        try:
            # Read original CSV
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Write to temp file with proper formatting
            with open(temp_file.name, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            
            # Send file
            return send_file(temp_file.name, as_attachment=True, download_name='CSE3_DBMS_team_details.csv', mimetype='text/csv')
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
    else:
        return "CSV file not found yet. Create some teams first!"
def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            # Test if port is available
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    return None

if __name__ == '__main__':
    # Try to find an available port
    port = find_available_port(5000)
    
    if port:
        print(f"Starting server on port {port}")
        print(f"Access the application at: http://127.0.0.1:{port}")
        print(f"CSV file will be created at: data/CSE3_DBMS_team_details.csv")
        app.run(debug=True, port=port)
    else:
        print("Error: Could not find an available port.")
        print("Please close some applications and try again.")