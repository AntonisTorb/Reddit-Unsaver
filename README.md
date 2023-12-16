# Reddit Unsaver
CLI app to unsave all saved posts from a Reddit account.

## Parameters

    -h, --help                            show this help message and exit
    -u USERNAME, --username USERNAME      Reddit username.
    -p PASSWORD, --password PASSWORD      Reddit password.

## How to use

With Python installed, open a terminal/CMD/PowerShell window and navigate to the directory containing the `reddit_unsaver.py` file, with the following command for example: `cd "path/"`

Make sure you install all the dependancies of the project with the command:

    pip install -r requirements.txt

In order to start the process you need to provide your Reddit username and password to the application. You can do this from the command line, by typing in the following command and replacing your credentials:

    python reddit_unsaver.py -u "username" -p "password"

Tha application will remove the saved posts one by one starting from the newest.


## Thank you and enjoy!