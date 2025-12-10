import sys
import os
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), 'edpy'))

with open('error_log.txt', 'w') as f:
    try:
        import edpy
        f.write(f"Import edpy successful. Dir: {dir(edpy)}\n")
        f.write(f"EdClient in edpy: {'EdClient' in dir(edpy)}\n")
    except Exception:
        traceback.print_exc(file=f)
