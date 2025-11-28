from flask import Flask, render_template, request, redirect, url_for, flash
from logic import load_data, save_data, add_student, run_assignment_algorithm

app = Flask(__name__)
app.secret_key = 'supersecretkey' # Needed for flash messages

@app.route('/')
def index():
    seminars, _ = load_data()
    return render_template('index.html', seminars=seminars)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    student_class = request.form.get('class')
    c1 = request.form.get('choice1')
    c2 = request.form.get('choice2')
    c3 = request.form.get('choice3')
    
    if not (name and student_class and c1 and c2 and c3):
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('index'))
    
    if len(set([c1, c2, c3])) < 3:
        flash('Please select 3 different seminars.', 'error')
        return redirect(url_for('index'))

    success, msg = add_student(name, student_class, [c1, c2, c3])
    if success:
        flash('Registration successful!', 'success')
    else:
        flash(msg, 'error')
        
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    seminars, students = load_data()
    
    # Calculate current stats
    seminar_stats = {s['id']: {'name': s['name'], 'capacity': s['capacity'], 'count': 0, 'students': []} for s in seminars}
    
    unassigned_students = []
    
    for s in students:
        if s['assigned_seminar_id']:
            seminar_stats[s['assigned_seminar_id']]['count'] += 1
            seminar_stats[s['assigned_seminar_id']]['students'].append(s)
        else:
            unassigned_students.append(s)
            
    return render_template('admin.html', seminars=seminars, stats=seminar_stats, unassigned=unassigned_students, students=students)

@app.route('/admin/assign', methods=['POST'])
def assign():
    result = run_assignment_algorithm()
    flash(f"Algorithm finished. Assigned: {result['assigned']}, Unassigned: {result['unassigned']}", 'info')
    return redirect(url_for('admin'))

@app.route('/admin/update_capacity', methods=['POST'])
def update_capacity():
    seminar_id = int(request.form.get('seminar_id'))
    new_capacity = int(request.form.get('capacity'))
    
    seminars, students = load_data()
    for s in seminars:
        if s['id'] == seminar_id:
            s['capacity'] = new_capacity
            break
    save_data(seminars, students)
    flash('Capacity updated.', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
