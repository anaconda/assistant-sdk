from conda.base.context import context
import os


def print_env_info(index, env_path):
    """Print information about a single environment"""
    try:
        # Get environment name
        env_name = os.path.basename(env_path)
        if env_name == "":
            env_name = os.path.basename(os.path.dirname(env_path))

        # Check if this is the base environment
        is_base = env_path == context.root_prefix
        if is_base:
            env_name = "base"

        # Check if environment exists and is accessible
        exists = os.path.exists(env_path)
        is_accessible = os.access(env_path, os.R_OK) if exists else False

        output = []
        output.append(f"{index:2d}. {env_name}")
        output.append(f"    Path: {env_path}")
        output.append(
            f"    Status: {'✓ Active' if exists and is_accessible else '✗ Inaccessible'}"
        )

        if exists and is_accessible:
            # Try to get Python version if available
            python_exe = os.path.join(env_path, "bin", "python")
            if os.path.exists(python_exe):
                try:
                    import subprocess

                    result = subprocess.run(
                        [python_exe, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        python_version = result.stdout.strip()
                        output.append(f"    Python: {python_version}")
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                    pass

        if is_base:
            output.append(f"    Type: Base Environment")

        output.append("")

        return "\n".join(output)

    except Exception as e:
        return f"    Error reading environment info: {e}\n"
