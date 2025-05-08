def get_clean_error_report_command(report: dict[str, str]) -> str:
    prefix = report["conda_info"]["conda_prefix"]

    # TODO
    # - convert `report["command"]` from relative to fully qualified path if starts with `./`

    command = report["command"]
    new_command = ""

    # print("conda_prefix\n", prefix)
    # print("command\n", prefix)

    # Remove the path from the command to only show 'conda'
    splitted = command.split()
    if splitted[0].endswith("conda"):
        new_command = "conda " + " ".join(splitted[1:])
        return new_command
    return command
