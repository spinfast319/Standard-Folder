# Standard-Folder (Beta)
### A python script that loops through your music directory and looks in each album folder. If it finds sub-directories it reneames the to a standard taxonomy.

There are many ways that people name subfolders inside music album folders.  Sub-direcotries with artwork can be named many things though artwork or covers are most common.  When releases are broken into multiple parts they are often named CD1, CD2 or Disc 1, Disc 2 but an almost infinite variety of approaches are taken.  This script seeks to standardize those folder names into a common taxonomy. The taxonomy is as follows:

- The script uses _Artwork_ for album related scans, covers, art, etc
- The script uses _Info_ for ripping info, lineage, reviews etc, 
- The script uses _CD1_, _CD2_, etc as the fomart for multiple discs.  

It uses [a file that maps most common aliases](https://github.com/spinfast319/Standard-Folder/blob/main/folder_map.txt) and some regular expressions to deal with common variants. The above preferences could easily be edited to fit your preferences in the script.  If the script encounters a sub directory that doesn't map to a known pattern it will first log it and then move the whole album to a folder where it can be edited by hand. It keeps track of what is renames and what it moves and provies a summary in the terminal as well as logging it. 

It is designed specifically for albums with artwork folders or multiple disc folders in them and ignores those without. It can also handle specials characters. It has been tested and works in Windows 10.

This script is meant to work in conjunction with other scripts in order to manage a large music library when the source of the music has good metadata you want to use to organize it.  You can find an overview of the scripts and workflow at [Origin-Music-Management](https://github.com/spinfast319/Origin-Music-Management). 

## Beta

This script is still in beta and has some known bugs especially moving albums with multiple subfolders in them.  If it is causing too many issues you can turn off the moving feature and just check the logs. The script also needs it's logging and summary text to be finalized. I might add some more regular expressions to automatically handle more variations of common folder names in the future as well.

## Install and set up
1) Clone this script where you want to run it.

2) Edit the script where it says _Set your directories here_ to set up or specify three directories you will be using. Write them as absolute paths for:

    A. The directory where the albums you want to examine for sub directories  
    B. The directory to store the log files the script creates  
    C. The directory where you want the albums with non standard folder names to be moved to.

3) Edit the script where it says _Set whether you are using nested folders_ to specify whether you are using nested folders or have all albums in one directory 

    A. If you have all your ablums in one music directory, ie. Music/Album then set this value to 1 (the default)  
    B. If you have all your albums nest in a Music/Artist/Album style of pattern set this value to 2

4) Edit the script where it says _Set whether you want to move folders that have missing final genre tags to a folders_ to specify whether you want to have ths script move albums with non standard folders to a different directory 

    A. If you want the script to move albums then set this value to True (the default)  
    B. If you do not want the albums to be moved set this value to False (they will still be logged)

5) Use your terminal to navigate to the directory the script is in and run the script from the command line.  When it finishes it will output any folders that were renamed, any non-standard folders it found and if it moves folders it will list both the original location and the new location.

```
Standard-Folder.py
```

_note: on linux and mac you will likely need to type "python3 FStandard-Folder.py"_  
_note 2: you can run the script from anywhere if you provide the full path to it_

The script will also create logs listing folders that were renamed, any non-standard folders it found and if it moves folders it will list all the albums it moved and include the original path and the new path.  

