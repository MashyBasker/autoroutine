create table if not exists courses (
    id serial primary key,
    name varchar(100) not null,
    weekly_hours integer,
    number_of_weeks integer
);

create table if not exists instructors (
    id serial primary key,
    name varchar(100) not null,
    time_preference varchar(100),
    weekday_preference varchar(100)
);

INSERT INTO courses (name, weekly_hours, number_of_weeks) VALUES
    ('Introduction to Computer Science', 4, 14),
    ('Data Structures and Algorithms', 5, 16),
    ('Database Management Systems', 4, 14),
    ('Operating Systems', 4, 14),
    ('Software Engineering', 4, 14),
    ('Computer Networks', 4, 14),
    ('Web Development', 4, 14),
    ('Machine Learning', 5, 16),
    ('Artificial Intelligence', 4, 14),
    ('Cybersecurity', 4, 14);
    
INSERT INTO instructors (name, time_preference, weekday_preference) VALUES
    ('Alice Smith', 'Morning', 'Monday, Wednesday, Friday'),
    ('Bob Johnson', 'Afternoon', 'Tuesday, Thursday'),
    ('Charlie Brown', 'Evening', 'Monday, Wednesday'),
    ('David Miller', 'Morning', 'Tuesday, Thursday'),
    ('Eva Davis', 'Afternoon', 'Monday, Wednesday, Friday'),
    ('Frank Wilson', 'Evening', 'Tuesday, Thursday'),
    ('Grace Lee', 'Morning', 'Monday, Wednesday'),
    ('Henry Clark', 'Afternoon', 'Tuesday, Thursday'),
    ('Ivy Anderson', 'Evening', 'Monday, Wednesday, Friday'),
    ('Jack Roberts', 'Morning', 'Tuesday, Thursday');
