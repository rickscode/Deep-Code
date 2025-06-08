from pathlib import Path

# Create core directories for the project
for subdir in [
    "src/core",
    "src/cli",
    "src/models",
    "src/operations",
    "src/plugins",
    "src/utils",
    "tests",
    "docs",
    "scripts",
    "configs"
]:
    Path(subdir).mkdir(parents=True, exist_ok=True)
