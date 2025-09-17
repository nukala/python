############################################################
# Experimental generated code. Utility unknown
############################################################
import os

def list_files(directory):
    try:
        # Get list of all items in directory
        items = os.listdir(directory)
        
        # Filter out unwanted files and directories
        filtered_items = [
            item for item in items
            if not item.startswith('.')  # Exclude hidden files starting with .
            and item not in {'.git', 'venv', '__pycache__'}  # Exclude specific folders
            and os.path.isfile(os.path.join(directory, item))  # Only include files
        ]
        
        # Print the filtered list
        for item in filtered_items:
            print(item)
            
    except FileNotFoundError:
        print(f"Directory '{directory}' not found.")
    except PermissionError:
        print(f"Permission denied accessing '{directory}'.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Use current directory (.) or specify a path
    list_files(".")

