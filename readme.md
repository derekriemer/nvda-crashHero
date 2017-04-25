
# How to use:
in the crash saver preferences,   there are two options.  There is an edit field with your current crashes directory in it. By activating the "pick  a directory" button, you can choose   where to house your crashes. Note that a crashes directory will be created under the directory you choose.
Now, click okay.
This is all! Next time NVDA crashes, A dialog will appear when it reboots itself. This dialog asks you what you were doing when NVDA crashed. Type what you were doing in a sentence or two. Good things to include here are:

* The app you were in.
* the thing you did in this app just before the crash.
* can you reproduce this crash reliably?
* What add-ons you were running (this may be convenient to add later).
* Any strange behavior NVDA exhibited before the crash.

In your chosen directory, you'll see a crashes directory. This directory contains timestamped folders that house all of your crashes. These folders also contain the first five words of the crash message you provided with any symbols not safe for folder names removed.
These crash directories, as they're called, contain 2 things.

* message.txt: The message you typed in the dialog.
* nvda_crash.dmp: The crash dump file NVDA generates when it dies.

I usually zip up the timestamped directory before sending the crash dump in.
