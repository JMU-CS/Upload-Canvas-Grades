import argparse
import configparser
import sys
from canvasapi import Canvas
import datetime
from collections import defaultdict
import pathlib

# logging.basicConfig(level=logging.INFO)

# module links look like this:
# https://canvas.jmu.edu/courses/2035460/modules/5197393


# https://stackoverflow.com/a/61901696
def get_datadir() -> pathlib.Path:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


def get_config(config_name):
    """Return the Path object for the config file, creating an empty file
    if it doesn't already exist.

    """
    config_dir = get_datadir() / "bulk_canvas_actions"
    try:
        config_dir.mkdir(parents=True)
    except FileExistsError:
        pass
    config_path = config_dir / config_name

    if not config_path.is_file():
        config_path.touch()

    return config_path


def move_assignments(all_assignment_groups, all_assignments):
    frm = int(input("Group to move from: "))
    to = int(input("Group to move to: "))
    start = int(input("Start item: "))
    end = int(input("End item: "))

    from_group = all_assignment_groups[frm]
    to_group = all_assignment_groups[to]

    assignments = []
    for assignment in all_assignments[all_assignment_groups[frm].id]:
        print(assignment)
        if assignment.position >= start and assignment.position <= end:
            assignments.append(assignment)

    assignment_names = "\n".join(str(i) for i in assignments)
    print(
        f"About to move:\n\n{assignment_names}\n\nfrom: {from_group}\nto:   {to_group}"
    )
    ok = input("OK? (Y/n): ")
    if len(ok) == 0 or ok.lower().startswith("y"):
        for assignment in assignments:
            print("Moving", assignment)
            print({"module_id": to_group.id})
            assignment.edit(assignment={"assignment_group_id": to_group.id})


def set_deadlines(all_assignment_groups, all_assignments):
    grp = int(input("Group to modify: "))
    start = int(input("Start item: "))
    end = int(input("End item: "))

    # read deadline date and time from user

    year = datetime.datetime.now().year
    month = int(input("Month: "))
    day = int(input("Day: "))
    hour = int(input("Hour (default 23): ") or 23)
    minute = int(input("Minute (default 59): ") or 59)
    deadline = datetime.datetime(year, month, day, hour, minute).isoformat()

    group = all_assignment_groups[grp]
    assignments = []
    for assignment in all_assignments[group.id]:
        print(assignment)
        if assignment.position >= start and assignment.position <= end:
            assignments.append(assignment)

    assignment_names = "\n".join(str(i) for i in assignments)
    print(f"About to set deadlines:\n\n{assignment_names}\n\nto: {deadline}")
    ok = input("OK? (Y/n): ")
    if len(ok) == 0 or ok.lower().startswith("y"):
        for assignment in assignments:
            print("Setting deadline for", assignment)
            print({"due_at": deadline})
            assignment.edit(assignment={"due_at": deadline})


def move_module_items(course):
    all_modules = {}
    for module in course.get_modules():
        print(f"{module.position}: {module}")
        all_modules[module.position] = module
        for item in module.get_module_items():
            print(f"\t {item.position}: {item}")
    frm = int(input("Module to move from: "))
    to = int(input("Module to move to: "))
    start = int(input("Start item: "))
    end = int(input("End item: "))

    from_module = all_modules[frm]
    to_module = all_modules[to]

    items = []
    for item in from_module.get_module_items():
        if item.position >= start and item.position <= end:
            items.append(item)

    item_names = "\n".join(str(i) for i in items)
    print(f"About to move:\n\n{item_names}\n\nfrom: {from_module}\nto:   {to_module}")
    ok = input("OK? (Y/n): ")
    if len(ok) == 0 or ok.lower().startswith("y"):
        for item in items:
            print("Moving", item)
            print({"module_id": to_module.id})
            item.edit(module_item={"module_id": to_module.id})


def bulk_edit_assignments(course):
    all_assignment_groups = {}
    for assignment_group in course.get_assignment_groups():
        all_assignment_groups[assignment_group.position] = assignment_group

    all_assignments = defaultdict(list)
    for assignment in course.get_assignments():
        all_assignments[assignment.assignment_group_id] += [assignment]

    for cur_group_pos in sorted(all_assignment_groups):
        cur_group = all_assignment_groups[cur_group_pos]
        print(f"{cur_group_pos}: {cur_group.name}")
        for assignment in all_assignments[cur_group.id]:
            print(f"\t{assignment.position}: {assignment.name}")

    todo = input("Move assignments (1) or set deadlines (2): ")
    if todo == "1":
        move_assignments(all_assignment_groups, all_assignments)
    elif todo == "2":
        set_deadlines(all_assignment_groups, all_assignments)


def main():
    parser = argparse.ArgumentParser(description="Bulk Cavnas actions.")

    parser.add_argument("--course-id", help="Canvas course id")

    parser.add_argument("--key-file", help="file that contains your Canvas key (oauth)")

    parser.add_argument("--key", help="your Canvas key (oauth)")

    parms = parser.parse_args()

    config_path = get_config("config.ini")

    config = configparser.ConfigParser()
    config.read(config_path)

    if parms.key is None and parms.key_file is None and "key" not in config["DEFAULT"]:
        print("No default key is cached. Must specify either a key or a key filename")
        sys.exit(0)

    update = False
    if parms.key_file is not None:
        f = open(parms.key_file, "r")
        key_lines = f.readlines()
        config["DEFAULT"]["key"] = key_lines[0].rstrip()
        update = True
    elif parms.key is not None:
        config["DEFAULT"]["key"] = parms.key
        update = True

    if parms.course_id is None and "course_id" not in config["DEFAULT"]:
        print("No default course id is cached. Must provide --course-id")
        sys.exit(0)

    if parms.course_id is not None:
        config["DEFAULT"]["course_id"] = parms.course_id
        update = True

    if update:
        print(f"Updating {config_path}")
        with open(config_path, "w") as configfile:
            config.write(configfile)

    canvas = Canvas("https://canvas.jmu.edu", config["DEFAULT"]["key"])
    course = canvas.get_course(config["DEFAULT"]["course_id"])

    todo = input("Move module items (1) or modify assignment groups or deadlines (2): ")
    if todo == "1":
        move_module_items(course)
    elif todo == "2":
        bulk_edit_assignments(course)


if __name__ == "__main__":
    main()
