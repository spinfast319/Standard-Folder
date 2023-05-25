#!/usr/bin/env python3

# Standardize Sub Directories
# author: hypermodified
# This python script loops through  your music directory and looks in each album folder. If it finds sub-directories it reneames the to a standard taxonomy.
# The taxonomy is Artwork, Info, CD1, CD2, etc.  It will maintain text after the CD seprated by a dash if it can.
# For albums that it can't make sense of it will log and move those to another directory for you to follow-up on later.
# It it designed to handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters.
# It has been tested and works in both and Windows 10.

# Import dependencies
import os  # Imports functionality that let's you interact with your operating system
import shutil  # Imports functionality that lets you copy files and directory
import datetime  # Imports functionality that lets you make timestamps
import re  # Imports functionality to use regular expressions
import shutil  # Imports functionality that lets you copy files and directory

import origin_script_library as osl  # Imports common code used across all origin scripts

#  Set the location of the local directory
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

#  Set your directory here
directory_to_check = "M:\PROCESS"  # Which directory do you want to start with?
log_directory = "M:\PROCESS-LOGS\Logs"  # Which directory do you want the log in?
sort_directory = "M:\PROCESS-SORT\Folders Non-standard"  # Directory to move albums with non standard folder names so you can manually fix them

# Set whether you are using nested folders or have all albums in one directory here
# If you have all your ablums in one music directory Music/Album_name then set this value to 1
# If you have all your albums nest in a Music/Artist/Album style of pattern set this value to 2
# The default is 1
album_depth = 2

# Set whether you want to move folders that have missing final genre tags to a folder so they can be dealt with manually later
# creates the list of albums that need to be moved post sorting
# If you want to move your albums set move_flag to True
# If you do NOT want to move your albums set move_flag to False
# The folders will be logged either way so you can always see which albums were missing final genre tags.
# The default is True
move_flag = True

# Establishes the counters for completed albums and missing origin files
total_count = 0
folder_count = 0
error_message = 0
rename_count = 0
nonstandard_folder = 0
renamed_folder = 0
move_count = 0


# identifies album directory level
path_segments = directory_to_check.split(os.sep)
segments = len(path_segments)
album_location = segments + album_depth

# creates the list of albums that need to be moved to be worked on later
move_list = []
folder_set = set()
rename_list = []
move_list_name = []


# A function to log events
def log_outcomes(directory, log_name, message, log_list):
    global log_directory

    script_name = "Standardize Folders Script"
    today = datetime.datetime.now()
    log_name = f"{log_name}.txt"
    album_name = directory.split(os.sep)
    album_name = album_name[-1]
    log_path = os.path.join(log_directory, log_name)
    with open(log_path, "a", encoding="utf-8") as log_name:
        log_name.write(f"--{today:%b, %d %Y} at {today:%H:%M:%S} from the {script_name}.\n")
        log_name.write(f"The album folder {album_name} {message}.\n")
        if log_list != None:
            log_name.write("\n".join(map(str, log_list)))
            log_name.write("\n")
        log_name.write(f"Album location: {directory}\n")
        log_name.write(" \n")
        log_name.close()


# A function that determines if there is an error
def error_exists(error_type):
    global error_message

    if error_type >= 1:
        error_message += 1  # variable will increment if statement is true
        return "Warning"
    else:
        return "Info"


# A function that writes a summary of what the script did at the end of the process
def summary_text():
    global count
    global total_count
    global error_message
    global track_count
    global missing_final_genre
    global move_count
    global flac_folder_count
    global nonstandard_folder
    global renamed_folder

    print("")
    print(f"This script wrote tags for {track_count} tracks in {count} folders out of {flac_folder_count} folders for {total_count} albums.")
    if move_count != []:
        print(f"The script moved {move_count} albums that non-standard folder names in them so you can fix them manually.")
    print("This script looks for potential missing files or errors. The following messages outline whether any were found.")

    error_status = error_exists(parse_error)
    print(f"--{error_status}: There were {parse_error} albums skipped due to not being able to open the yaml. Redownload the yaml file.")
    error_status = error_exists(origin_old)
    print(f"--{error_status}: There were {origin_old} origin files that do not have the needed metadata and need to be updated.")
    error_status = error_exists(bad_missing)
    print(f"--{error_status}: There were {bad_missing} folders missing an origin files that should have had them.")
    error_status = error_exists(missing_genre_origin)
    print(f"--{error_status}: There were {missing_genre_origin} folders missing genre tags in their origin files.")
    error_status = error_exists(missing_final_genre)
    print(f"--{error_status}: There were {missing_final_genre} albums where a genere tag could not be mapped and was missing. Fix these manually.")
    error_status = error_exists(good_missing)
    print(f"--Info: Some folders didn't have origin files and probably shouldn't have origin files. {good_missing} of these folders were identified.")

    if error_message >= 1:
        print("Check the logs to see which folders had errors and what they were and which tracks had metadata written to them.")
    else:
        print("There were no errors.")


# A function to check whether the directory is a an album or a sub-directory
def level_check(directory):
    global total_count
    global album_location

    print("")
    print(directory)
    print("Folder Depth:")
    print(f"--The albums are stored {album_location} folders deep.")

    path_segments = directory.split(os.sep)
    directory_location = len(path_segments)

    print(f"--This folder is {directory_location} folders deep.")

    # Checks to see if a folder is an album or subdirectory by looking at how many segments are in a path
    if album_location == directory_location:
        print("--This is an album.")
        total_count += 1  # variable will increment every loop iteration
        return True
    elif album_location < directory_location:
        print("--This is a sub-directory")
        return False
    elif album_location > directory_location and album_depth == 2:
        print("--This is an artist folder.")
        return False


def collect_directory(directory, album_location):
    global folder_count
    global folder_set

    subfolders = [f.name for f in os.scandir(directory) if f.is_dir()]
    if subfolders:
        for i in subfolders:
            folder_set.add(i)
    folder_count += 1  # variable will increment every loop iteration


def standardize_directory(directory, album_location, folder_map):
    global rename_list
    global nonstandard_folder
    global renamed_folder
    global move_list

    skip_list = ["Artwork", "Info"]

    subfolders = [f.name for f in os.scandir(directory) if f.is_dir()]
    if subfolders:
        print("Go forth and standardize.")
        print("--Subfolders Present:")
        for i in subfolders:
            match_flag = False
            print(f"----{i}")
            if i in skip_list:
                print(f"----{i} is the correct folder name.")
                print("No subfolders to standardize.")
                match_flag = True
                pass
            elif re.match(r"\bCD(\d+)\b", i):
                print(f"----{i} is the correct folder name.")
                print("No subfolders to standardize.")
                match_flag = True
                pass
            elif re.match(r"^CD(\d+) \- ", i):
                print(f"----{i} is the correct folder name.")
                print("No subfolders to standardize.")
                match_flag = True
                pass
            else:
                for j in folder_map:
                    if i == j[1]:
                        print(f"----Matching: {i} is the same as {j[1]}.")
                        print(f"----Rename: {i} to {j[0]}.")
                        match_flag = True
                        old_name = i
                        new_name = j[0]
                        old_path = os.path.join(directory, i)
                        new_path = os.path.join(directory, j[0])

                        # make the pair a tupple
                        rename_paths = (old_path, new_path, old_name, new_name)
                        # adds the tupple to the list
                        rename_list.append(rename_paths)

                        # log the folders that got renamed
                        print(f"--Logged folder that got renamed: {i} to {j[0]}")
                        log_name = "renamed_folder"
                        log_message = f"had a folder that got renamed:  {i} to {j[0]}"
                        log_list = None
                        log_outcomes(directory, log_name, log_message, log_list)
                        renamed_folder += 1  # variable will increment every loop iteration
                    else:
                        pass

            if match_flag == False:
                # adds the non-standard directory name to the list
                old_name = os.path.join(directory, i)
                move_list_name.append(old_name)
                # log the folders that don't match a known pattern for manual intervention
                print(f"--Logged folder that doesn't match a known pattern: {i}")
                log_name = "nonstandard_folder"
                log_message = f"has a folder that does not match a known pattern: {i}"
                log_list = None
                log_outcomes(directory, log_name, log_message, log_list)
                nonstandard_folder += 1  # variable will increment every loop iteration
                move_location(directory)
    else:
        print("No subfolders to standardize.")


def load_folder_map():

    folder_map_list = []

    file = open(os.path.join(__location__, "folder_map.txt"), "r")

    for line in file.readlines():
        fname = line.rstrip().split(",")  # using rstrip to remove the \n
        folder_map_list.append(fname)

    return folder_map_list


# A function to rename folders from the non-standard names to the standard ones
def rename_folders(rename_list):
    global rename_count

    # Loop through the list of albums to rename
    for i in rename_list:

        # Break each entry into the old name and the new name
        old_path = i[0]
        new_path = i[1]
        old_name = i[2]
        new_name = i[3]

        # List the final path conventions so you can deal with OS case insensitivity before you check to see if a folder is identical
        swap_case_list = ["artwork", "info"]

        print("")
        print("Renaming.")

        # Check swap out case sensitive names that are identical
        if old_name in swap_case_list:
            # Rename them
            print(f"--Source: {old_path}")
            print(f"--Destination: {new_path}")
            os.rename(old_path, new_path)
            print("Renaming completed.")
        elif re.match(r"^cd(\d+) \- ", old_name):
            # Rename them
            print(f"--Source: {old_path}")
            print(f"--Destination: {new_path}")
            os.rename(old_path, new_path)
            print("Renaming completed.")
        elif re.match(r"\bcd(\d+)\b", old_name):
            # Rename them
            print(f"--Source: {old_path}")
            print(f"--Destination: {new_path}")
            os.rename(old_path, new_path)
            print("Renaming completed.")
        # Check to see if a folder of the same name already exists in the directory
        elif os.path.exists(new_path):
            print("--Checking to see if there is a folder with the same name already.")
            print(f"--A directory with the name {new_name} already exists in this folder.")
            print(f"--Copying files from {old_name} to {new_name}.")
            # gather all files
            allfiles = os.listdir(old_path)
            for f in allfiles:
                src_path = os.path.join(old_path, f)
                print(src_path)
                dst_path = os.path.join(new_path, f)
                print(dst_path)
                # check to see if a file with the same name exists
                if os.path.exists(dst_path):
                    # renames and moves files
                    print("--A file with the same name already exists, renaming file.")
                    newf = "new_" + f
                    new_src_path = os.path.join(old_path, newf)
                    os.rename(src_path, new_src_path)
                    new_dst_path = os.path.join(new_path, newf)
                    # moves files
                    print(f"--Moving files")
                    shutil.move(new_src_path, new_dst_path)
                else:
                    # moves files
                    print(f"--Moving files")
                    shutil.move(src_path, dst_path)
            # delete old directory
            print("--Deleting old directory.")
            os.rmdir(old_path)
            print("Renaming completed.")
        else:
            print(f"--A directory with the name {new_name} does not exist in this folder.")
            # Rename them
            print(f"--Source: {old_path}")
            print(f"--Destination: {new_path}")
            os.rename(old_path, new_path)
            print("Renaming completed.")

        rename_count += 1  # variable will increment every loop iteration


# A function to build the location the files should be moved to
def move_location(directory):
    global sort_directory
    global move_list
    global album_depth

    print(f"MOVE SOURCE: {directory}")
    # create target path

    # get album name or artist-album name and create target path
    path_parths = directory.split(os.sep)
    if album_depth == 1:
        album_name = path_parths[-1]
        target = os.path.join(sort_directory, album_name)
        print(f"MOVE TARGET: {target}")
    elif album_depth == 2:
        artist_name = path_parths[-2]
        album_name = path_parths[-1]
        target = os.path.join(sort_directory, artist_name, album_name)
        print(f"MOVE TARGET: {target}")

    print("--This should be moved to the Genre Sort folder and has been added to the move list.")
    # make the pair a tupple
    print(directory)
    print(target)
    move_pair = (directory, target)
    # adds the tupple to the list
    move_list.append(move_pair)


# A function to move albums to the correct folder
def move_albums(move_list):
    global move_count

    # Loop through the list of albums to move
    for i in move_list:

        # Break each entry into a source and target
        start_path = i[0]
        target = i[1]

        # Move them to the folders they belong in
        print("")
        print("Moving.")
        print(f"--Source: {start_path}")
        print(f"--Destination: {target}")
        shutil.move(start_path, target)
        print("Move completed.")
        move_count += 1  # variable will increment every loop iteration


def write_list(folder_set):
    global list_directory

    list_name = "unique_subfolders.txt"
    list_path = os.path.join(list_directory, list_name)

    with open(list_path, "a", encoding="utf-8") as list_name:
        list_name.write(" \n")
        list_name.write("Unique Subfolders \n")
        list_name.write("----------------- \n")
        list_name.write("\n".join(folder_set))
        list_name.write(" ")
        list_name.write(" \n")
        list_name.close()


# The main function that controls the flow of the script
def main():
    global move_list
    global folder_set
    global album_location
    global rename_list
    global rename_count
    global album_depth

    # Get all the subdirectories of album_directory recursively and store them in a list
    directories = osl.set_directory(directory_to_check)

    # Load the folder_map list
    folder_map = load_folder_map()

    #  Run a loop that goes into each directory identified in the list and identifies folders that need to be renamed or moved
    for i in directories:
        os.chdir(i)  # Change working Directory
        # establish directory level
        is_album = level_check(i)

        # make a filter for itunes and musicbee folders
        path_segments = i.split(os.sep)
        if album_depth == 1:
            parent_folder = path_segments[-1]
        elif album_depth == 2:
            parent_folder = path_segments[-2]

        if parent_folder == "iTunes":
            pass
        elif parent_folder == "MusicBee":
            pass
        else:
            # standardize folder names
            if is_album:
                standardize_directory(i, album_location, folder_map)  # Run your function

    # Change directory so the folders can be renamed and moved
    os.chdir(log_directory)

    print("")
    print("Part 2: Renaming")

    # Rename the folders
    if rename_list == []:
        print("--No folders needed renaming.")
    else:
        rename_folders(rename_list)

    # List non-standard folder names
    print("")
    print("Part 3: Non-standard folder names")
    if move_list_name == []:
        print("--No folders had non-standard names.")
    else:
        for i in move_list_name:
            print(f"--{i}")

    # Move the albums to the folders the need to be sorted into
    if move_flag == True:

        # Change directory so the album directory can be moved and move them
        os.chdir(log_directory)

        print("")
        print("Part 4: Moving")

        # Move the albums
        if move_list == []:
            print("--No albums needed moving.")
        else:
            print(move_list)
            # move_albums(move_list)

    print("")
    print(f"This script renamed {rename_count} folders.")

    """# Print the list of unique subfolders.
    print("")
    print("Unique Subfolders")
    folder_set = sorted(folder_set)
    print ('\n'.join(folder_set))
    print("")
    print(f"This script looked in {folder_count} folders for subfolders.")   
      

    # Write the subfolder names to a text file
    #write_list(folder_set)   """


if __name__ == "__main__":
    main()
