# My Journal #

## 10/4/2023 ##
Today I tried to package the project using the `pyinstaller` module. I was able to create a single executable file, but it didn't work. I don't know why.
I alos tried running py setup.py but it just packages the original git-cola project. I even tried running things like "py setup.py clean" and "py setup.py build" but it didn't work. 

## 10/5/2023 ##
Today I messed with the setup.py file that I somehow didn't see. I ran the command "py setup.py install" which installed the entire project as a package that can (I think) be distributed! so now if I go anywhere on my computer, I can use the "cola" command and it will pull up the gui with the autofill button.
Also, I made a small change to my prompt so now it knows the project name. I think I may add the project description to the prompt as well.

Here's me running the command in the terminal:
![command](./images/command.png)

Here's the gui with the autofill button that comes from the command:
![gui](./images/gui.png)