import os

def get_workspace_dir() -> str:
    """Auto-detects active platform workspace: Kaggle (/kaggle/working), Colab (/content), or CWD."""
    if "WORKSPACE_DIR" in os.environ:
        return os.environ["WORKSPACE_DIR"]
    if os.path.exists("/kaggle/working"):
        return "/kaggle/working"
    if os.path.exists("/content"):
        return "/content"
    return os.getcwd()

WORKSPACE_DIR = get_workspace_dir()
