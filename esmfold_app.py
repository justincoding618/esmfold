import streamlit as st
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio

st.sidebar.title('ESMFold')
st.sidebar.write('[*ESMFold*](https://esmatlas.com/about) is an end-to-end single sequence protein structure predictor based on the ESM-2 language model.  You can learn more from the [research article](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v2) and the [news article](https://www.nature.com/articles/d41586-022-03539-1) published in *Nature*.')

# set up stmol
def render_molecule(pdb):
	pdbview = py3Dmol.view()
	pdbview.addModel(pdb,'pdb')
	pdbview.setStyle({'cartoon':{'color':"spectrum"}})
	pdbview.setBackgroundColor('black')
	pdbview.zoomTo()
	pdbview.zoom(2, 800)
	pdbview.spin(True)
	showmol(pdbview, height = 500, width = 800)

# Inputing Protein Sequence
DEFAULT_SEQ = "Insert your protein sequence here"
txt = st.sidebar.text_area('Input Sequence', DEFAULT_SEQ, height=275)