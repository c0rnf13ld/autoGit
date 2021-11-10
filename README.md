# autoGit
This script is focused on when we have a .git on a page that we are auditing. 
## About the script
This script is oriented to clone the repository of a page, first we must confirm that it has a .git, then see if you can read the HEAD file located in .git/logs/HEAD, if these requirements are met we can see the commits of the same and we can clone the entire repository and see the source code of the page.
## Requirements:
```
apt-get install git -y
pip3 install colorama requests
```
