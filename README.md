# Preparing environment and installing the utility
*Tested on Ubuntu Desktop 20.10 (64bit), Python3.8*

First, create a directory for the application, *cd* to it, [download](https://github.com/efibutov/home_work) the assignment.
(Any way you like - git, https or zip archive).

In order to prevent dependencies clash with your "system-wide" packages, we highly recommend using of [virtual environment](https://docs.python.org/3/tutorial/venv.html).

After installing **venv**, activate it:
```
source venv/bin/activate
```
Next, install dependencies:
```
pip install -r requirements.txt
```

For some reasons, official repository *PyPi* experiences some issues. If you have a problem with installing packages from this
repository, try alternative PyPi packages repository. For example, this worked for us very well:
```
pip install -r requirements.txt -i https://pypi.douban.com/simple
```
Be careful when installing software from unknown sources (as in example above)!

Please, follow instructions for installing **Pillow** (required dependency) [here](https://pillow.readthedocs.io/en/stable/installation.html).

---
# Using the utility

*cd* to working dir (where the utility's code and venv dir reside), activate virtual environment if needed, and run
```
python main.py
```
This will make the required job - parse tables, download images, and, finally, produce the output html file
with all related info.

# Settings

There are some settings in the **settings.py** file - look at it and play with some settings (relevant both for user and developer).

---
# License

Use it on your own risk. Feel free to do with this code any use. No restrictions or rules.

---
# Feedback and contacts

For bugfixes, questions, propositions,
feature requests, thanks, etc. :) please email me to [Efi Butovski](mailto:efibutov@gmail.com).

**2021.03.24 13:57**
