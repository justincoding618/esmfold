import streamlit as st
from stmol import showmol
import py3Dmol
import time
import requests
import biotite.structure.io as bsio

st.sidebar.title('ESMFold')
st.sidebar.write('[*ESMFold*](https://esmatlas.com/about) is an end-to-end single sequence protein structure predictor based on the ESM-2 language model. You can learn more from the [research article](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v2) and the [news article](https://www.nature.com/articles/d41586-022-03539-1) published in *Nature*.')

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
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            st.info(f"Attempting to contact ESMFold API... (Attempt {attempt + 1}/{max_attempts})")
            
            response = requests.post(
                'https://api.esmatlas.com/foldSequence/v1/pdb/',
                data=sequence,
                timeout=300
            )
            
            if response.status_code == 200:
                pdb_string = response.text
                
                if 'ATOM' in pdb_string and len(pdb_string) > 100:
                    st.success("Structure prediction successful!")
                    
                    with open('predicted.pdb', 'w') as f:
                        f.write(pdb_string)
                    
                    structure = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
                    b_value = round(structure.b_factor.mean(), 4)
                    
                    st.subheader('Visualization of Predicted Protein Structure')
                    render_molecule(pdb_string)
                    
                    st.subheader('pLDDT')
                    st.write('pLDDT is a per-residue estimate of the confidence in prediction on a scale from 0-100.')
                    st.info(f'pLDDT: {b_value}')
                    
                    st.download_button(
                        label="Download PDB",
                        data=pdb_string,
                        file_name='predicted.pdb',
                        mime='text/plain'
                    )
                    return
                    
            st.warning(f"Attempt {attempt + 1} failed. Retrying...")
            time.sleep(5)
            
        except Exception as e:
            st.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(5)
    
    st.error("⚠️ ESMFold API is currently unavailable after multiple attempts.")

predict = st.sidebar.button('Predict', on_click=update)

# File upload option (outside the button callback)
st.markdown("---")
st.subheader("Alternative: Upload Pre-computed PDB File")
st.info("If the API is down, you can generate structures using [ColabFold](https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb) and upload the PDB file here.")

uploaded_file = st.file_uploader("Upload PDB file", type=['pdb'])

if uploaded_file is not None:
    pdb_string = uploaded_file.read().decode('utf-8')
    
    with open('predicted.pdb', 'w') as f:
        f.write(pdb_string)
    
    structure = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
    b_value = round(structure.b_factor.mean(), 4)
    
    st.subheader('Visualization of Uploaded Protein Structure')
    render_molecule(pdb_string)
    
    st.subheader('pLDDT')
    st.write('pLDDT is a per-residue estimate of the confidence in prediction on a scale from 0-100.')
    st.info(f'pLDDT: {b_value}')
    
    st.download_button(
        label="Download PDB",
        data=pdb_string,
        file_name='predicted.pdb',
        mime='text/plain'
    )

if not predict and uploaded_file is None:
    st.warning('Please enter your protein sequence and click Predict, or upload a PDB file!')