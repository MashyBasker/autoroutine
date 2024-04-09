import tkinter as tk
from tkinter import messagebox
import database
from timetable import gen_timetable

class TimetableGUI:
    def __init__(self, master, conn):
        self.master = master
        self.conn = conn
        self.master.title("Timetable Generator")
        self.master.configure(bg="#f0f0f0")

        # Add padding and increase font size
        self.label = tk.Label(master, text="Enter Course Name:", bg="#f0f0f0", font=("Arial", 12))
        self.label.pack(pady=5)

        self.course_name_entry = tk.Entry(master, font=("Arial", 12))
        self.course_name_entry.pack(pady=5)

        self.label2 = tk.Label(master, text="Enter Instructor Name:", bg="#f0f0f0", font=("Arial", 12))
        self.label2.pack(pady=5)

        self.instructor_name_entry = tk.Entry(master, font=("Arial", 12))
        self.instructor_name_entry.pack(pady=5)

        self.label3 = tk.Label(master, text="Enter Room Number:", bg="#f0f0f0", font=("Arial", 12))
        self.label3.pack(pady=5)

        self.room_number_entry = tk.Entry(master, font=("Arial", 12))
        self.room_number_entry.pack(pady=5)

        # Use a different color for buttons
        self.insert_button = tk.Button(master, text="Insert Data", command=self.insert_data, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.insert_button.pack(pady=10)

        self.generate_button = tk.Button(master, text="Generate Timetable", command=self.generate_timetable, bg="#008CBA", fg="white", font=("Arial", 12))
        self.generate_button.pack(pady=10)

    def insert_data(self):
        course_name = self.course_name_entry.get()
        instructor_name = self.instructor_name_entry.get()
        room_number = self.room_number_entry.get()

        try:
            # Insert data into the database
            database.insert_course_data(self.conn, course_name, instructor_name, room_number)
            messagebox.showinfo("Success", "Data inserted successfully!")

            # Clear entry fields for next input
            self.course_name_entry.delete(0, tk.END)
            self.instructor_name_entry.delete(0, tk.END)
            self.room_number_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def generate_timetable(self):
        # Generate timetable
        gen_timetable()
        messagebox.showinfo("Success", "Timetable generated successfully!")

def main():
    # Initialize SQLite database
    conn = database.connect_to_database()
    database.create_tables(conn)

    # Create the GUI window
    root = tk.Tk()
    root.geometry("1000x700")  # Set window size
    root.configure(bg="#f0f0f0")  # Set background color

    app = TimetableGUI(root, conn)
    root.mainloop()

if __name__ == "__main__":
    main()
