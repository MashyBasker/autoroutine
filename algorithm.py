import numpy as np
import csv
import random
from prettytable import PrettyTable
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

NUM_GENERATIONS = 300  # Number of generations
POPULATION_SIZE = 100  # Population size
MUTATION_RATE = 1.5  # Mutation rate
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
MAX_LAB_HOURS = 3
TIMESLOTS = [
    "9am-10am",
    "10am-11am",
    "11am-12pm",
    "12pm-1pm",
    "2pm-3pm",
    "3pm-4pm",
    "4pm-5pm"
]

# Read data from CSV files
def read_data(file_paths):
    rooms = set()
    classes = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                classes.append(row)
                rooms.add(row['Room'])
    return classes, len(rooms)

# Define the chromosome representation
class Chromosome:
    def __init__(self, semester_data):
        self.schedule = []
        self.num_rooms = semester_data['num_rooms']  # Store the number of rooms
        self.classes = semester_data['classes']  # Store the classes data
        
        # Initialize the schedule to include each class at least once
        for class_data in self.classes:
            room = random.randint(1, self.num_rooms)
            day = random.choice(DAYS_OF_WEEK)
            class_type = class_data['ClassType']
            weekly_hours = int(class_data['WeeklyHours'])

            # Adjust weekly hours for lab classes
            if class_type == 'Lab':
                weekly_hours = MAX_LAB_HOURS

            # Schedule the class for the appropriate number of hours
            for _ in range(weekly_hours):
                timeslot = random.choice(range(len(TIMESLOTS)))
                self.schedule.append((class_data, room, timeslot, day))


    def mutate(self):
        # Check if there are unused courses
        unused_courses = [course for course in self.classes if course not in [c[0] for c in self.schedule]]

        if unused_courses:
            # Add a random unused course to the schedule
            new_course = random.choice(unused_courses)
            room = random.randint(1, self.num_rooms)
            day = random.choice(DAYS_OF_WEEK)
            
            # Determine the class type and adjust weekly hours accordingly
            if new_course['ClassType'] == 'Lab':
                weekly_hours = MAX_LAB_HOURS
            else:
                weekly_hours = 4  # Adjust the number of hours for Theory classes as needed

            # Ensure that the course is not scheduled on the same day of the week at the same timeslot
            while any(c[3] == day and c[2] in range(6, len(TIMESLOTS)) for c in self.schedule if c[0]['Course'] == new_course['Course'] and c[0]['ClassType'] == new_course['ClassType']):
                day = random.choice(DAYS_OF_WEEK)

            # Find an available timeslot within the 3 PM to 5 PM range
            available_timeslots = [i for i in range(6, len(TIMESLOTS))]
            timeslot = random.choice(available_timeslots)

            # Schedule the course for consecutive hours
            for j in range(weekly_hours):
                if timeslot + j >= len(TIMESLOTS):
                    break  # Check if the timeslot exceeds the available timeslots
                self.schedule.append((new_course, room, timeslot + j, day))
        else:
            # Mutation: randomly change a class schedule
            idx = random.randint(0, len(self.schedule) - 1)
            course_data, room, timeslot, day = self.schedule[idx]  # Unpack course data, room, timeslot, and day
            class_type = course_data['ClassType']
            weekly_hours = int(course_data['WeeklyHours'])

            # Calculate remaining weekly hours for the course
            remaining_hours = weekly_hours - sum(1 for c in self.schedule if c[0] == course_data and c[1] == room and c[2] == timeslot and c[3] == day)

            # Check if the selected class is a lab class
            is_lab = class_type == 'Lab'

            if is_lab or class_type == 'Theory':
                # Find available consecutive timeslots for lab or theory classes
                available_slots = [i for i in range(len(TIMESLOTS) - remaining_hours + 1) if all(self.schedule[idx + j][1] is None for j in range(remaining_hours))]
                if not available_slots:
                    return  # No valid timeslots available for lab or theory class
                timeslot = random.choice(available_slots)

                # Ensure that the course is not scheduled on the same day of the week at the same timeslot
                while any(c[3] == day and c[2] == timeslot for c in self.schedule if c[0]['Course'] == course_data['Course'] and c[0]['ClassType'] == course_data['ClassType']):
                    day = random.choice(DAYS_OF_WEEK)

                # Ensure that classes are scheduled for consecutive hours
                for j in range(remaining_hours):
                    if timeslot + j >= len(TIMESLOTS):
                        break  # Check if the timeslot exceeds the available timeslots
                    self.schedule[idx + j] = (course_data, room, timeslot + j, day)

                # Update the remaining entries to be empty for the same time slots
                for k in range(len(self.schedule)):
                    if k != idx and self.schedule[k][2] in range(timeslot, timeslot + remaining_hours) and self.schedule[k][3] == day:
                        self.schedule[k] = (None, None, None, None)

    # Helper method to find a valid timeslot for a course
    def find_valid_timeslot(self, course_data, room):
        # Find a valid timeslot for a course that occurs daily at the same time
        timeslot = random.choice(range(len(TIMESLOTS)))
        while any(c[1] == room and c[2] == timeslot for c in self.schedule):
            timeslot = random.choice(range(len(TIMESLOTS)))
        return timeslot


# Define fitness function
def fitness(chromosome):
    fitness_score = 0
    
    # Create dictionaries to track class assignments to rooms and instructors for each day of the week
    room_schedule = {}
    for room in range(1, chromosome.num_rooms + 1):
        room_schedule[room] = {day: [False] * len(TIMESLOTS) for day in DAYS_OF_WEEK}
    instructor_schedule = {}
    for instructor in set(class_data['Instructor'] for class_data, _, _, day in chromosome.schedule):
        instructor_schedule[instructor] = {day: [False] * len(TIMESLOTS) for day in DAYS_OF_WEEK}
    course_hours = {}

    # Initialize course_hours dictionary
    for class_data, _, _, _ in chromosome.schedule:
        course_key = (class_data['Course'], class_data['ClassType'])
        course_hours[course_key] = 0

    # Calculate fitness based on constraints
    for (class_data, room, timeslot, day) in chromosome.schedule:
        instructor = class_data['Instructor']
        class_type = class_data['ClassType']
        hours = int(class_data['WeeklyHours'])
        
        # Constraint 1: Check if the room is available
        if room_schedule[room][day][timeslot]:
            fitness_score -= 1
        else:
            for t in range(timeslot, min(timeslot + hours, len(TIMESLOTS))):
                if t >= len(room_schedule[room][day]):
                    room_schedule[room][day].extend([False] * (t - len(room_schedule[room][day]) + 1))  # Extend list if needed
                if room_schedule[room][day][t]:
                    fitness_score -= 1
                room_schedule[room][day][t] = True
        
        # Constraint 2: Check if the instructor is available
        if instructor_schedule[instructor][day][timeslot]:
            fitness_score -= 1
        else:
            for t in range(timeslot, min(timeslot + hours, len(TIMESLOTS))):
                if t >= len(instructor_schedule[instructor][day]):
                    instructor_schedule[instructor][day].extend([False] * (t - len(instructor_schedule[instructor][day]) + 1))  # Extend list if needed
                if instructor_schedule[instructor][day][t]:
                    fitness_score -= 1
                instructor_schedule[instructor][day][t] = True
        
        # Constraint 3: Lab classes cannot exceed 3 hours and should be consecutive
        if class_type == 'Lab':
            if hours != MAX_LAB_HOURS or timeslot + hours > len(TIMESLOTS):
                fitness_score -= 2
            for t in range(timeslot, timeslot + hours):
                if t >= len(room_schedule[room][day]) or t >= len(instructor_schedule[instructor][day]):
                    room_schedule[room][day].extend([False] * (t - len(room_schedule[room][day]) + 1))  # Extend lists if needed
                    instructor_schedule[instructor][day].extend([False] * (t - len(instructor_schedule[instructor][day]) + 1))
                if room_schedule[room][day][t] or instructor_schedule[instructor][day][t]:
                    fitness_score -= 1
                room_schedule[room][day][t] = True
                instructor_schedule[instructor][day][t] = True
        
        # Constraint 4: Check if the total hours for each course do not exceed the weekly hours
        course_key = (class_data['Course'], class_data['ClassType'])
        course_hours[course_key] += hours
        if course_hours[course_key] > hours * 2:  # Allow for some overlap to account for mutations
            fitness_score -= 1
        
        # Constraint 5: Check if courses are scheduled on different days of the week
        if any(c[3] == day for c in chromosome.schedule if c[0]['Course'] == class_data['Course'] and c[0]['ClassType'] == class_data['ClassType'] and c != (class_data, room, timeslot, day)):
            fitness_score -= 1
    
    # Constraint 6: Check if the number of courses scheduled on each day is balanced
    num_courses_per_day = [sum(1 for c in chromosome.schedule if c[3] == day) for day in DAYS_OF_WEEK]
    max_num_courses = max(num_courses_per_day)
    min_num_courses = min(num_courses_per_day)
    if max_num_courses - min_num_courses > 1:  # Allow for some imbalance to account for mutations
        fitness_score -= 1
    
    return fitness_score



# Generate and display timetable
def generate_timetable(schedule):
    timetable_table = PrettyTable()
    timetable_table.field_names = ['Time'] + DAYS_OF_WEEK

    timetable_grid = {day: [''] * len(TIMESLOTS) for day in DAYS_OF_WEEK}

    for (class_data, room, timeslot, day) in schedule:
        course_info = f"{class_data['Course']} ({class_data['ClassType']})"
        timetable_grid[day][timeslot] = course_info

    for i, timeslot in enumerate(TIMESLOTS):
        row_data = [timeslot]
        for day in DAYS_OF_WEEK:
            row_data.append(timetable_grid[day][i])
        timetable_table.add_row(row_data)

    for field in timetable_table.field_names:
        timetable_table.align[field] = 'l'

    return timetable_table


# Main loop for even semesters
# Define a list to store timetables
all_timetables = []

# Main loop for even semesters
for semester in [2, 4, 6, 8]:
    file_paths = [f"sem{semester}.csv"]
    classes, num_rooms = read_data(file_paths)
    semester_data = {'classes': classes, 'num_rooms': num_rooms}
    
    population = [Chromosome(semester_data) for _ in range(POPULATION_SIZE)]
    best_fitness = float('-inf')  # Track the best fitness
    generations_without_improvement = 0  # Counter for generations without improvement
    
    for generation in range(NUM_GENERATIONS):
        fitness_scores = [(chromosome, fitness(chromosome)) for chromosome in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)

        # Check if the best fitness improves
        if fitness_scores[0][1] > best_fitness:
            best_fitness = fitness_scores[0][1]
            generations_without_improvement = 0  # Reset counter
        else:
            generations_without_improvement += 1

        # Debug print statements
        print(f"Semester {semester}, Generation {generation}: Best fitness = {best_fitness}, Generations without improvement = {generations_without_improvement}")

        # Terminate if there's no improvement for a certain number of generations
        if generations_without_improvement >= 20:  # Adjust the threshold as needed
            print("Terminating due to no improvement in fitness for 20 generations.")
            break

        parents = [random.choice(fitness_scores[:POPULATION_SIZE // 2]) for _ in range(POPULATION_SIZE // 2)]
        offspring = []

        for parent1, parent2 in zip(parents[::2], parents[1::2]):
            if len(parent1[0].schedule) == 1:
                crossover_point = 0
            else:
                crossover_point = random.randint(1, len(parent1[0].schedule) - 1)
            child1 = Chromosome(semester_data)
            child1.schedule = parent1[0].schedule[:crossover_point] + parent2[0].schedule[crossover_point:]
            child2 = Chromosome(semester_data)
            child2.schedule = parent2[0].schedule[:crossover_point] + parent1[0].schedule[crossover_point:]
            offspring.extend([child1, child2])

        for child in offspring:
            if random.random() < MUTATION_RATE:
                child.mutate()

        population = offspring

    
    best_schedule = fitness_scores[0][0]
    timetable = generate_timetable(best_schedule.schedule)
    all_timetables.append((f"Timetable for Semester {semester}:", timetable))
    print(f"Timetable for Semester {semester} generated.")

for title, table in all_timetables:
    print(title)
    print(table)
    print()
    
def pretty_table_to_reportlab(pretty_table):
    data = [pretty_table.field_names] + pretty_table._rows
    reportlab_table = Table(data)
    reportlab_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                          ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                          ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                          ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    return reportlab_table

# Create a PDF
doc = SimpleDocTemplate("timetables.pdf", pagesize=letter)

# List to hold flowables
flowables = []

# Iterate through all timetables
for title, pretty_table in all_timetables:
    # Convert PrettyTable to ReportLab table
    reportlab_table = pretty_table_to_reportlab(pretty_table)
    
    # Add title to the flowables
    title_paragraph = Paragraph(title, ParagraphStyle(name='Title'))
    flowables.append(title_paragraph)
    flowables.append(reportlab_table)

# Build the PDF
doc.build(flowables)
