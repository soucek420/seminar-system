import json
import os
import random
from datetime import datetime

SEMINARS_FILE = 'seminars.json'
STUDENTS_FILE = 'students.json'

def load_data():
    if not os.path.exists(SEMINARS_FILE):
        return [], []
    with open(SEMINARS_FILE, 'r', encoding='utf-8') as f:
        seminars = json.load(f)
    
    if not os.path.exists(STUDENTS_FILE):
        students = []
    else:
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            students = json.load(f)
            
    return seminars, students

def save_data(seminars, students):
    with open(SEMINARS_FILE, 'w', encoding='utf-8') as f:
        json.dump(seminars, f, indent=4, ensure_ascii=False)
    with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=4, ensure_ascii=False)

def add_student(name, student_class, choices):
    seminars, students = load_data()
    
    # Check if student already exists (simple check by name)
    for s in students:
        if s['name'] == name and s['class'] == student_class:
            return False, "Student already registered."

    new_student = {
        'id': len(students) + 1,
        'name': name,
        'class': student_class,
        'choices': [int(c) for c in choices], # List of seminar IDs [1st, 2nd, 3rd]
        'assigned_seminar_id': None,
        'timestamp': datetime.now().isoformat()
    }
    students.append(new_student)
    save_data(seminars, students)
    return True, "Registration successful."

def run_assignment_algorithm():
    seminars, students = load_data()
    
    # Reset assignments
    for s in students:
        s['assigned_seminar_id'] = None
    
    # Create a map for easier access to seminar data
    seminar_map = {s['id']: s for s in seminars}
    # Track current counts
    seminar_counts = {s['id']: 0 for s in seminars}
    
    # Sort students by timestamp (First Come First Served base logic)
    # Although the user said "higher priority", usually that means choice 1 > choice 2.
    # Within the same choice level, we need a tie-breaker. Timestamp is fair.
    students.sort(key=lambda x: x['timestamp'])

    # Round 1: Try to assign 1st choice
    unassigned_round_1 = []
    for student in students:
        choice_id = student['choices'][0]
        if seminar_counts[choice_id] < seminar_map[choice_id]['capacity']:
            student['assigned_seminar_id'] = choice_id
            seminar_counts[choice_id] += 1
        else:
            unassigned_round_1.append(student)
            
    # Round 2: Try to assign 2nd choice for those unassigned
    unassigned_round_2 = []
    for student in unassigned_round_1:
        choice_id = student['choices'][1]
        if seminar_counts[choice_id] < seminar_map[choice_id]['capacity']:
            student['assigned_seminar_id'] = choice_id
            seminar_counts[choice_id] += 1
        else:
            unassigned_round_2.append(student)

    # Round 3: Try to assign 3rd choice
    unassigned_final = []
    for student in unassigned_round_2:
        choice_id = student['choices'][2]
        if seminar_counts[choice_id] < seminar_map[choice_id]['capacity']:
            student['assigned_seminar_id'] = choice_id
            seminar_counts[choice_id] += 1
        else:
            unassigned_final.append(student)
            
    # Save results
    save_data(seminars, students)
    
    return {
        'total_students': len(students),
        'assigned': len(students) - len(unassigned_final),
        'unassigned': len(unassigned_final),
        'unassigned_list': [s['name'] for s in unassigned_final]
    }
