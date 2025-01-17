Static HTML file browser for github pages
====================================

Screenshot about output
------------------
![screenshot not available](screenshot.png?raw=true)

About the program
------------
This program can generate html files to every directory in your Dropbox/Public folder (or any other shared folder) and makes it possible to navigate online between these directories when it looks like an output of apache web server.

Requirements
-------------------
* Linux
* Python 3.x
* The following modules must be installed:
  + jinja2
  + unipath

Installation
------------
1. Before starting the program, please edit the config.py with your favourite text editor. Setting up takes less than 30 seconds if you read the comments in config.py
2. Now start program.py with -h or --help command line argument. There will be a short info about it.
    ```python program.py --help```
3. Use "program.py --install location" command, and it will copy "icons" directory to the specified directory.
    ```python program.py --install ~/Dropbox/Public/```
4. Start the program with a location command line argument, which is the path of the Public folder of your Dropbox directory.
    ```python program.py ~/Dropbox/Public/```
5. Try it out! Share the link of the index.html file which is in the root directory of Dropbox/Public folder. You can open it with a webbrowser or you can share it on the internet.

Changes / to-do
------------
* Add option to enable recursing into directories or not
* Add option to run in daemon mode (eg from crontab repeatedly)
* make basic stuff (everything except "Open" column) completely independent of http links
* Remove mention of dropbox - it does not support html rendering anymore
* Do not overwrite unless specifically configured (via flag or config)
* Change icon folder name to something more uncommon on destination
* Merge --install function to default usage
* When index.html, overwrite onlyif existing html was written by this program
* Add option to ignore some extensions

Contributors
----------------
[Jabba Laci](https://github.com/jabbalaci)

[Iváncza Csaba](https://github.com/icsaba)

[Fábián Rita](https://github.com/frita21)
