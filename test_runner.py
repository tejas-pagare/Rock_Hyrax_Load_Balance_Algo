import sys
# Add the current directory to the path to find the modules
sys.path.append('.')
from main import main

if __name__ == '__main__':
    # Mock the command-line arguments
    sys.argv = ['main.py', '--skip-interactive']
    main()
