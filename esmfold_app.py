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

# The ESMFold Application
def update(sequence=txt):
	headers = {
	'Content-Type': 'application/w-www-form-urlencoded'
	}
	response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb', headers=headers, data=sequence)
	name = sequence[:3] + sequence[-3:]
	pdb_string = response.content.decode('utf-8')

	with open('predicted.pdb', 'w') as function:
		function.write(pdb_string)

	structure = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
	b_value = round(structure.b_factor.mean(), 4)

	#Display Protein Structure
	st.subheader('Visualization of Predicted Protein Structure')
	render_molecule(pdb_string)

	#Get p1DDT Values; p1DDT is stored in B-factor field
	st.subheader('p1DDT')
	st.write('p1DDT is a per-residue of the confidence in prediction on a scale from 1-100.')
	st.info(f'p1DDT: {b_value}')

	st.download_button(
		label="Download PDB",
		data=pdb_string,
		file_name='predicted_pdb',
		mime='text/plain'
		)

predict = st.sidebar.button('Predict', on_click=update)

if not predict:
	st.warning('Please enter your protein sequence data!')

