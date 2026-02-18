
import datetime
import os
import re
import shutil
import subprocess
import sys

def get_current_version():
    """Read version from django_kickstart/__init__.py"""
    with open("django_kickstart/__init__.py", "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'__version__ = "(\d+\.\d+\.\d+)"', content)
    if not match:
        raise ValueError("Could not find version in django_kickstart/__init__.py")
    return match.group(1)

def increment_patch_version(version):
    """Increment the patch version (x.y.z -> x.y.z+1)"""
    major, minor, patch = map(int, version.split("."))
    return f"{major}.{minor}.{patch + 1}"

def update_file_version(filepath, old_version, new_version):
    """Replace version string in a file"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = content.replace(old_version, new_version)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {filepath}: {old_version} -> {new_version}")

def run_command(command, fail_message):
    """Run a shell command and exit on failure"""
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError:
        print(f"Error: {fail_message}")
        sys.exit(1)

def prompt_changelog():
    """Prompt user for changelog entries."""
    print("\n📝 Enter changelog entries for this release.")
    print("   Type one entry per line. Press Enter on an empty line to finish.")
    print("   (Pres CTRL+C to cancel release)")
    
    entries = []
    while True:
        try:
            entry = input(f"   - ").strip()
            if not entry:
                break
            entries.append(entry)
        except KeyboardInterrupt:
            print("\n❌ Release cancelled.")
            sys.exit(0)
    
    return entries

def update_changelog_file(version, entries):
    """Prepend new version entry to CHANGELOG.md"""
    if not entries:
        print("⚠ No changelog entries provided. Skipping CHANGELOG.md update.")
        return

    changelog_path = "CHANGELOG.md"
    today = datetime.date.today().isoformat()
    
    new_entry = f"\n## [{version}] — {today}\n\n### 🚀 Changes\n"
    for entry in entries:
        new_entry += f"- {entry}\n"
    
    if not os.path.exists(changelog_path):
        # Create new changelog if missing
        content = f"# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n---{new_entry}"
        print(f"Created {changelog_path}")
    else:
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Insert after the first horizontal rule (---)
        if "---" in content:
            parts = content.split("---", 1)
            content = f"{parts[0]}---{new_entry}{parts[1]}"
        else:
            # Fallback: append to top if no '---' found (unlikely given standard format)
            content = f"{new_entry}\n{content}"
            
        print(f"Updated {changelog_path}")

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    # 1. Get current version
    current_version = get_current_version()
    new_version = increment_patch_version(current_version)
    
    print(f"🚀 Preparing release: {current_version} -> {new_version}")
    
    # 2. Prompt for Changelog
    changes = prompt_changelog()
    
    # 3. Update files
    update_file_version("django_kickstart/__init__.py", current_version, new_version)
    update_file_version("pyproject.toml", current_version, new_version)
    update_changelog_file(new_version, changes)
    
    # 4. Clean dist/
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("Cleaned dist/ directory")
    
    # 5. Build
    print("📦 Building package...")
    run_command("python -m build", "Failed to build package")
    
    # 6. Upload
    print(f"⬆️ Uploading version {new_version} to PyPI...")
    # Using twine to upload. Assumes user has credentials set up or will enter them.
    run_command("twine upload dist/*", "Failed to upload to PyPI")
    
    print(f"✅ Successfully released version {new_version}!")

if __name__ == "__main__":
    main()
