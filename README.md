# esmfold
This ESMFold application is a bioinformatics app that predicts protein structures of a given amino acid sequence.  If the API is down, there is an alternative option where you can use the Google Colab Notebook that utilizes the AlphaFold2 model (you will see the hyperlink when you run the app).  You can paste the sequence there and download the results and upload the pdb file to display the results.

## Running the Application Locally
The first thing you'll need to do is create a virtrual environment to run your streamlit app.  You will need to install Anaconda (or miniconda can work if you want to do custom setups yourself).  After installing Anaconda (or miniconda), you will then setup the virtual environment as mentioned in the steps here:  https://docs.streamlit.io/get-started/installation/anaconda-distribution

Alternatively, you can also install a streamlit virtual enviornment in the terminal, which you can find here:  https://docs.streamlit.io/get-started/installation/command-line

Once you have setup your vitrual environement, if you set it up through the Anaconda Navigator, you will need to activate the virtual environment through the Anaconda Navigator.  If you setup the virtual environment through commands, you will run the command `conda activate [yourstreamlitenv_name]` (replace with your virtual environment name).

## Installing Libraries for Your Virtual Environment
Along with setting up your virtual environment, you will need to install the following (outside your virtual envrionment and within your working machine) for the virtual environment to work:

* `pip install streamlit`
* `pip install stmol`
* `pip install py3Dmol`
* `pip install requests`
* `pip install biotite`
* `pip install pyautogui`

You may need to install additional libraries if necessary (the command output will tell you which ones you need if you don't have them).  Alternatively, you can create the requirements.txt file to type in all the needed libraries and use the requirements.txt file and type `pip install requirements.txt` to install all the necessary libraries.

## Running the Application
After installing the libraries and activating the enviornment, you will then run your application by typing `streamlit run esmfold_app.py`.  Running this command will open the app locally through your browser.  You should then be able to play with the application!

## Acknowledgements
Special thanks goes to the following:

* <a href="https://github.com/dkoes">David Koes</a> for innovating the py3Dmol plugin.
* <a href="https://github.com/dataprofessor">Data Professor</a> for coming up with the idea of making an ESMFold-like prediction application.


