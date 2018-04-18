import sys

try:
    import foodSense
except ImportError:
    print('Error importing foodSense module')
    sys.exit(1)

if __name__ == '__main__':
    #Start GUI
    foodSense()
