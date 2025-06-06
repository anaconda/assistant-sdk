def get_clean_error_report_command(report: dict) -> str:
    prefix = report["conda_info"]["conda_prefix"]

    # NOTE:
    # We might want to use `report["conda_info"]["conda_prefix"]` along with `report["command"]` to
    # be a little more robust about removing the path from the command. Othwerise, it's possible the
    # naive soluton below could fail if the command is not in the form of
    # `prefix/conda <command>`.

    command = report["command"]
    new_command = ""

    # Remove the path from the command to only show 'conda'
    splitted = command.split()
    if splitted[0].endswith("conda"):
        new_command = "conda " + " ".join(splitted[1:])
        return new_command
    return command
