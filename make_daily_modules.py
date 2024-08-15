from canvasapi import Canvas
import datetime
import calendar

API_KEY = "19~CxJxQziptazTYY0dJkrZUoj86Vy3RvOQsW0AIJWitHun02Wu4zvpkj5rJVMounlZ"
COURSE_ID = 2035460


def main():
    canvas = Canvas("https://canvas.jmu.edu", API_KEY)
    course = canvas.get_course(COURSE_ID)

    start = datetime.date(2024, 8, 21)
    end = datetime.date(2024, 12, 6)
    cur_date = start
    ok_days = [0, 2, 4]
    names = calendar.day_name
    position = 1

    while cur_date <= end:
        if cur_date.weekday() in ok_days:
            name = f"{names[cur_date.weekday()]} {cur_date.month}/{cur_date.day}/{cur_date.year}"
            course.create_module({"position": position, "name": name})
            print({"position": position, "name": name})

            position += 1

        cur_date += datetime.timedelta(days=1)


if __name__ == "__main__":
    main()
