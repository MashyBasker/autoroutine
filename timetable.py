import numpy as np
import random
import database
from prettytable import PrettyTable

# Initialize SQLite database
conn = database.connect_to_database()
database.create_tables(conn)

# Create tables for storing timetable and other data
# courses_data = [
#     (1, "Introduction to Computer Science", 1, 1, "Room 101", ""),
#     (2, "Data Structures and Algorithms", 2, 2, "Room 102", ""),
#     (3, "Computer Networks", 2, 3, "Room 103", ""),
#     (4, "Operating Systems", 2, 4, "Room 104", ""),
#     (5, "Database Management Systems", 2, 5, "Room 105", ""),
#     (6, "Software Engineering", 2, 6, "Room 106", ""),
#     (7, "Artificial Intelligence", 2, 7, "Room 107", ""),
#     (8, "Machine Learning", 2, 8, "Room 108", ""),
#     (9, "Web Development", 2, 9, "Room 109", ""),
#     (10, "Computer Graphics", 2, 10, "Room 110", ""),
#     # Add more courses as needed
# ]

# instructors_data = [
#     (1, "Dr. Smith", "Morning"),
#     (2, "Prof. Johnson", "Afternoon"),
#     (3, "Dr. Lee", "Evening"),
#     (4, "Prof. Wang", "Morning"),
#     (5, "Dr. Garcia", "Afternoon"),
#     (6, "Prof. Brown", "Evening"),
#     (7, "Dr. Kim", "Morning"),
#     (8, "Prof. Martinez", "Afternoon"),
#     (9, "Dr. Nguyen", "Evening"),
#     (10, "Prof. Taylor", "Morning"),
#     # Add more instructors as needed
# ]

# # Insert sample data into courses table
# database.insert_courses_data(conn, courses_data)
# database.insert_instructors_data(conn, instructors_data)

# Define genetic algorithm functions

def generate_random_timetable(conn, num_days, num_time_slots):
    timetable = {}

    # Retrieve all courses from the database
    courses = database.get_all_courses_with_instructors(conn)

    # Initialize timetable with empty slots
    for day in range(1, num_days + 1):
        for time_slot in range(1, num_time_slots + 1):
            timetable[(day, time_slot)] = None

    # Assign courses randomly to timetable slots
    for course in courses:
        day = random.randint(1, num_days)
        time_slot = random.randint(1, num_time_slots)
        timetable[(day, time_slot)] = course

    return timetable


def fitness_function(timetable):
    conflicts = 0

    # Retrieve all courses from the database
    courses = database.get_all_courses_with_instructors(conn)

    # Count conflicts
    for slot1, course_id1 in timetable.items():
        for slot2, course_id2 in timetable.items():
            if slot1 != slot2 and course_id1 is not None and course_id2 is not None:
                # Find course details from courses data
                course1 = next((course for course in courses if course[0] == course_id1), None)
                course2 = next((course for course in courses if course[0] == course_id2), None)
                if course1 is not None and course2 is not None:
                    # Check if courses overlap
                    if (course1[0] == course2[0] and
                            slot1[0] == slot2[0] and
                            slot1[1] != slot2[1]):
                        conflicts += 1

    # Calculate fitness score
    fitness_score = 1 / (1 + conflicts)  # Higher fitness for fewer conflicts
    return fitness_score



def crossover(timetable1, timetable2):
    # Convert dictionaries to lists of tuples sorted by keys
    timetable1_list = sorted(timetable1.items())
    timetable2_list = sorted(timetable2.items())

    # Perform crossover
    crossover_point = random.randint(1, len(timetable1_list) - 1)
    child1_list = timetable1_list[:crossover_point] + timetable2_list[crossover_point:]
    child2_list = timetable2_list[:crossover_point] + timetable1_list[crossover_point:]

    # Convert lists back to dictionaries
    child1 = dict(child1_list)
    child2 = dict(child2_list)

    return child1, child2


def mutate(timetable, courses_data, mutation_rate, num_days, num_time_slots):
    mutated_timetable = timetable.copy()

    # Mutate randomly
    for day in range(1, num_days + 1):
        for time_slot in range(1, num_time_slots + 1):
            if random.random() < mutation_rate:
                # Randomly select a course from the available courses
                new_course = random.choice(courses_data)
                new_course_id = new_course[0]  # Assuming course ID is the first element
                mutated_timetable[(day, time_slot)] = new_course_id

    return mutated_timetable

def select_parents(population, fitness_scores):
    """Select parents for crossover."""
    # Select parents using tournament selection
    tournament_size = min(5, len(population))  # Ensure tournament size is not larger than population
    parents = []
    for _ in range(2):
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[np.argmax(tournament_fitness)]
        parents.append(population[winner_index])
    return parents

def display_timetable(conn, timetable):
    # Retrieve all courses and instructors from the database
    courses = database.get_all_courses_with_instructors(conn)
    instructors = database.get_all_instructors(conn)

    # Create a list of days and times of day
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    times_of_day = ["1. Morning", "2. Afternoon", "3. Evening"]

    # Create a dictionary to map instructors to their IDs
    instructor_id_to_name = {instructor[0]: instructor[1] for instructor in instructors}

    # Create a table to display the timetable
    table = PrettyTable([""] + days_of_week)

    # Initialize the table with empty cells
    for time_of_day in times_of_day:
        table.add_row([time_of_day] + [""] * len(days_of_week))

    # Track added courses for summary at the bottom
    added_courses = {}

    # Fill in the table with course name and room number
    for (day, time_slot), course_id in timetable.items():
        course_info = next((course for course in courses if course[0] == course_id), None)
        # print(course_info)
        if course_info:
            _, course_name, _, _, room_number, _ = course_info
            # Convert day to string representation
            day_str = days_of_week[day - 1] if 1 <= day <= len(days_of_week) else "Unknown"
            time_slot_str = times_of_day[time_slot - 1] if 1 <= time_slot <= len(times_of_day) else "Unknown"
            for row_index, time_of_day in enumerate(times_of_day):
                if time_slot_str == time_of_day:
                    break
            else:
                continue
            for col_index, day_of_week in enumerate(days_of_week):
                if day_str == day_of_week:
                    break
            else:
                continue
            # Add course name and room number to the table
            table.add_row([""] * (col_index + 1) + [f"{course_name}\n({room_number})"] + [""] * (len(days_of_week) - col_index - 1))
            # Add course and instructor to the added_courses dictionary
            added_courses[course_name] = instructor_id_to_name.get(course_info[2], "Unknown Instructor")

    # Display the timetable
    print(table)

    # Display added courses summary
    print("\nCourses added to the timetable:")
    for course_name, instructor_name in added_courses.items():
        print(f"{course_name} - {instructor_name}")

def gen_timetable():
    # Parameters
    num_days = 5
    num_time_slots = 3  # Morning, Afternoon, Evening
    mutation_rate = 0.1
    population_size = 100
    num_generations = 100

    # Retrieve course data from the database
    courses_data = database.get_all_courses_with_instructors(conn)

    # Initialize population
    population = [generate_random_timetable(conn, num_days, num_time_slots) for _ in range(population_size)]

    # Genetic algorithm main loop
    for generation in range(num_generations):
        # Evaluate fitness of each individual
        fitness_scores = [fitness_function(timetable) for timetable in population]

        # Select parents for crossover
        parents = select_parents(population, fitness_scores)

        # Crossover and mutation
        offspring = []
        for i in range(0, len(parents), 2):
            child1, child2 = crossover(parents[i], parents[i+1])
            child1 = mutate(child1, courses_data, mutation_rate, num_days, num_time_slots)
            child2 = mutate(child2, courses_data, mutation_rate, num_days, num_time_slots)
            offspring.extend([child1, child2])

        # Replace old population with offspring
        population = offspring

        # Display best timetable in each generation
        best_timetable_index = np.argmax(fitness_scores)
        if best_timetable_index < len(population):  # Check if best_timetable_index is within bounds
            best_timetable = population[best_timetable_index]
            print(f"Generation {generation+1}, Best Fitness: {fitness_scores[best_timetable_index]}")
            display_timetable(conn, best_timetable)
        else:
            print(f"Generation {generation+1}: Best timetable index out of range.")
            break  # Break out of the loop if best_timetable_index is out of range

