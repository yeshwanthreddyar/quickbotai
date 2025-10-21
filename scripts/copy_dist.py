
import os, shutil, sys

def copytree(src, dst):
    if not os.path.isdir(src):
        print(f"Source not found: {src}")
        sys.exit(1)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"Copied {src} -> {dst}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/copy_dist.py <path_to_frontend_dist> <dest_web_dir>")
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2]
    copytree(src, dst)
