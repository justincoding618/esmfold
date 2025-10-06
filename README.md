# esmfold
A bioinformatics app that predicts protein structures of a given amino acid sequence.  The project is inspired by the Data Professor on YouTube.

## Running the Application Locally
The first thing you'll need to do is create a virtrual environment to run your streamlit app.  You will need to install Anaconda (or miniconda can work if you want to do custom setups yourself).  After installing Anaconda (or miniconda), you will then setup the virtual environment as mentioned in the steps here:  https://docs.streamlit.io/get-started/installation/anaconda-distribution

Alternatively, you can also install a streamlit virtual enviornment in the terminal, which you can find here:  https://docs.streamlit.io/get-started/installation/command-line

Once you have setup your vitrual environement, you will run the command `conda activate [yourstreamlitenv_name]`.

## Installing Libraries to Your Virtual Environment
Once you have activated your virtual environment, you will need to install the following:

* `pip install streamlit`
* `pip install stmol`
* `pip install py3Dmol`
* `pip install requests`
* `pip install biotite`

You may need to install additional libraries if necessary (the command output will tell you which ones you need if you don't have them).

## Running the Application
After installing the libraries and activating the enviornment, you will then run your application by typing `streamlit run esmfold_app.py`.  Running this command will open the app locally through your browser.  You should then be able to play with the application!

