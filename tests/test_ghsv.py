import pytest
import os
import tempfile
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from ghsv import (
    run_shell_command, 
    get_uncommitted_files, 
    collect_full_backup, 
    collect_visible_non_ignored, 
    create_backup_zip
)

def test_run_shell_command_success():
    output = run_shell_command("echo test")
    assert output == "test"

def test_run_shell_command_failure():
    with pytest.raises(RuntimeError, match="Command 'invalid_cmd' failed"):
        run_shell_command("invalid_cmd")

def test_run_shell_command_timeout():
    with pytest.raises(TimeoutError, match="timed out"):
        run_shell_command("sleep 2", timeout=1)

def test_run_shell_command_with_log(tmp_path):
    log_file = tmp_path / "log.txt"
    output = run_shell_command("echo test", log_file=log_file)
    assert output == "test"
    with open(log_file, "r") as f:
        assert "Command: echo test" in f.read()

@pytest.fixture
def temp_git_repo():
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        run_shell_command("git init")
        with open("file1.txt", "w") as f:
            f.write("content")
        with open(".hidden.txt", "w") as f:
            f.write("hidden")
        run_shell_command("git add file1.txt")
        run_shell_command("git commit -m 'Initial commit'")
        with open("file2.txt", "w") as f:
            f.write("uncommitted")
        yield tmp_dir

def test_get_uncommitted_files(temp_git_repo):
    files = get_uncommitted_files(temp_git_repo)
    assert os.path.join(temp_git_repo, "file2.txt") in files
    assert os.path.join(temp_git_repo, "file1.txt") not in files

def test_get_uncommitted_files_empty(temp_git_repo):
    run_shell_command("git add .")
    run_shell_command("git commit -m 'Add all'")
    files = get_uncommitted_files(temp_git_repo)
    assert files == []

def test_collect_full_backup(temp_git_repo):
    files = collect_full_backup(temp_git_repo)
    assert os.path.join(temp_git_repo, "file1.txt") in files
    assert os.path.join(temp_git_repo, ".hidden.txt") in files
    assert any(".git" in f for f in files)

def test_collect_visible_non_ignored(temp_git_repo):
    files = collect_visible_non_ignored(temp_git_repo)
    assert os.path.join(temp_git_repo, "file1.txt") in files
    assert os.path.join(temp_git_repo, "file2.txt") in files
    assert os.path.join(temp_git_repo, ".hidden.txt") not in files
    assert not any(".git" in f for f in files)

def test_create_backup_zip_full(tmp_path, temp_git_repo):
    zip_path = create_backup_zip(temp_git_repo, "full", str(tmp_path))
    assert zip_path.endswith(f"__{Path(temp_git_repo).parent.name}__{datetime.now().strftime('%y%b%d').lower()}.zip")
    with zipfile.ZipFile(zip_path, "r") as zf:
        assert "file1.txt" in zf.namelist()
        assert ".hidden.txt" in zf.namelist()

def test_create_backup_zip_visible(tmp_path, temp_git_repo):
    zip_path = create_backup_zip(temp_git_repo, "visible", str(tmp_path))
    with zipfile.ZipFile(zip_path, "r") as zf:
        assert "file1.txt" in zf.namelist()
        assert "file2.txt" in zf.namelist()
        assert ".hidden.txt" not in zf.namelist()

def test_create_backup_zip_uncommitted(tmp_path, temp_git_repo):
    zip_path = create_backup_zip(temp_git_repo, "uncommitted", str(tmp_path))
    with zipfile.ZipFile(zip_path, "r") as zf:
        assert "file2.txt" in zf.namelist()
        assert "file1.txt" not in zf.namelist()

def test_create_backup_zip_empty_folder(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    zip_path = create_backup_zip(str(empty_dir), "full", str(tmp_path))
    assert zip_path is None

def test_create_backup_zip_invalid_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_backup_zip("/invalid/path", "full", str(tmp_path))

def test_create_backup_zip_invalid_mode(tmp_path, temp_git_repo):
    with pytest.raises(ValueError, match="Invalid backup mode"):
        create_backup_zip(temp_git_repo, "invalid", str(tmp_path))
