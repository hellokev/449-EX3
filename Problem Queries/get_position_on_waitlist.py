from collections import OrderedDict

def get_position_on_waitlist(dict, student_id):
    ordered_dict = OrderedDict({k: v for k, v in sorted(dict.items(), key=lambda item: item[1])})
    return list(ordered_dict.keys()).index(student_id) + 1


waitlist = {
    "11111111": "2023-09-16 09:00:00",
    "22222222": "2023-09-15 11:00:00",
    "3333333": "2023-09-15 10:00:00",
    "4444444": "2023-09-16 12:00:00",
    "5555555": "2023-09-15 15:30:00",
    "6666666": "2023-09-17 08:45:00",
    "7777777": "2023-09-15 14:15:00"
}
sorted = get_position_on_waitlist(waitlist, "11111111")

print(sorted)