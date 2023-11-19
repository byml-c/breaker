def convert_time_schedule(schedule):
    timetable = [
        "8:00", "8:50",
        "9:00", "9:50",
        "10:10", "11:00",
        "11:10", "12:00",
        "14:00", "14:50",
        "15:00", "15:50",
        "16:10", "17:00",
        "17:10", "18:00",
        "18:30", "19:20",
        "19:30", "20:20",
        "20:30", "21:20"
    ]

    converted_schedule = []

    for entry in schedule:
        day_index, start_class, end_class = entry
        start_time = timetable[start_class - 1]
        end_time = timetable[end_class]

        day_output = [
            day_index,
            int(start_time.split(':')[0]) * 3600 + int(start_time.split(':')[1]) * 60,
            int(end_time.split(':')[0]) * 3600 + int(end_time.split(':')[1]) * 60
        ]

        converted_schedule.append(day_output)

    return converted_schedule

# 给定的数据
schedule_data = [
    [0, 5, 6],
    [0, 7, 8],
    [0, 9, 10],
    [0, 11, 12],
    [0, 13, 14],
    [0, 15, 16],
    [1, 5, 6],
    [1, 7, 8],
    [1, 17, 18],
    [1, 19, 20],
    [2, 3, 4],
    [2, 5, 6],
    [2, 11, 12],
    [2, 13, 14],
    [3, 17, 18],
    [3, 1, 2],
    [3, 3, 4],
    [3, 5, 6],
    [3, 13, 14],
    [3, 15, 16],
    [3, 17, 18],
    [3, 17, 18],
    [4, 11, 12],
    [4, 13, 14],
    [4, 15, 16]
]

converted_result = convert_time_schedule(schedule_data)
print(converted_result)
