def read_version(file_path="version.properties"):
    version_info = {}
    with open(file_path, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            version_info[key.strip()] = value.strip()

    major = version_info.get("major", "0")
    minor = version_info.get("minor", "0")
    patch = version_info.get("patch", "0")

    return f"{major}.{minor}.{patch}"