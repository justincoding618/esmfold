import streamlit as st
from stmol import showmol
import py3Dmol
import time
import requests
import biotite.structure.io as bsio
import re
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="ESMFold Protein Structure Predictor", layout="wide")

# Initialize session state
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None
if 'pdb_string' not in st.session_state:
    st.session_state.pdb_string = None

st.sidebar.title('ESMFold')
st.sidebar.write('[*ESMFold*](https://esmatlas.com/about) is an end-to-end single sequence protein structure predictor based on the ESM-2 language model. You can learn more from the [research article](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v2) and the [news article](https://www.nature.com/articles/d41586-022-03539-1) published in *Nature*.')

# Validation function
def validate_sequence(sequence):
    """Validate protein sequence input"""
    # Remove whitespace and convert to uppercase
    sequence = re.sub(r'\s+', '', sequence.upper())
    
    # Handle FASTA format
    if sequence.startswith('>'):
        lines = sequence.split('\n')
        sequence = ''.join(lines[1:])
    
    # Check if empty
    if not sequence or sequence == "Insert your protein sequence here":
        return None, "Please enter a protein sequence"
    
    # Check for valid amino acids
    valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
    invalid_chars = set(sequence) - valid_aa
    if invalid_chars:
        return None, f"Invalid amino acids found: {', '.join(sorted(invalid_chars))}"
    
    # Check length
    if len(sequence) > 400:
        return None, f"Sequence is {len(sequence)} amino acids. Sequence is too long.  You can only put up to 400 amino acids."
    elif len(sequence) < 10:
        return None, "Sequence is too short (minimum 10 amino acids)"
    
    return sequence, None

# Visualization function with options
def render_molecule(pdb, color_scheme='spectrum', spin=True):
    pdbview = py3Dmol.view(width=800, height=500)
    pdbview.addModel(pdb, 'pdb')
    
    if color_scheme == 'spectrum':
        pdbview.setStyle({'cartoon': {'color': 'spectrum'}})
    elif color_scheme == 'chain':
        pdbview.setStyle({'cartoon': {'colorscheme': 'chain'}})
    elif color_scheme == 'secondary':
        pdbview.setStyle({'cartoon': {'colorscheme': 'ssJmol'}})
    
    pdbview.setBackgroundColor('black')
    pdbview.zoomTo()
    pdbview.zoom(2, 800)
    if spin:
        pdbview.spin(True)
    showmol(pdbview, height=500, width=800)

# Function to plot pLDDT scores
def plot_plddt_scores(structure):
    """Create a plot of per-residue pLDDT scores"""
    residue_ids = list(range(1, len(structure.b_factor) + 1))
    plddt_scores = structure.b_factor
    
    # Color by confidence level
    colors = ['#FF0000' if score < 50 else 
              '#FFAA00' if score < 70 else 
              '#AAFF00' if score < 90 else 
              '#00FF00' for score in plddt_scores]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=residue_ids,
        y=plddt_scores,
        marker_color=colors,
        name='pLDDT'
    ))
    
    fig.update_layout(
        title='Per-Residue Confidence (pLDDT)',
        xaxis_title='Residue Position',
        yaxis_title='pLDDT Score',
        yaxis_range=[0, 100],
        height=300,
        showlegend=False
    )
    
    # Add confidence level annotations
    fig.add_hline(y=90, line_dash="dash", line_color="green", 
                  annotation_text="Very High (>90)")
    fig.add_hline(y=70, line_dash="dash", line_color="orange", 
                  annotation_text="High (>70)")
    fig.add_hline(y=50, line_dash="dash", line_color="red", 
                  annotation_text="Low (>=50), Very Low (<50)",
                  )
    
    return fig

# Sidebar input
st.sidebar.subheader("Input Options")
st.sidebar.write('You can either try your own amino acid sequence or an example.')

# Example sequences
EXAMPLES = {
    "Select an example...": "",
    "Insulin": "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN",
    "Lysozyme": "KVFGRCELAAAMKRHGLDNYRGYSLGNWVCAAKFESNFNTQATNRNTDGSTDYGILQINSRWWCNDGRTPGSRNLCNIPCSALLSSDITASVNCAKKIVSDGNGMNAWVAWRNRCKGTDVQAWIRGCRL",
    "Hemoglobin Alpha": "VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR",
    "Hemoglobin Delta": "VHLTPEEKTAVNALWGKVNVDAVGGEALGRLLVVYPWTQRFFESFGDLSSPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNLKGTFSQLSELHCDKLHVDPENFRLLGNVLVCVLARNFGKEFTPQMQAAYQKVVAGVANALAHKYH",
    "Small Peptide": "MKTIIALSYIFCLVFADYKD",
    "Large Peptide": "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
}

# Example selector
example_choice = st.sidebar.selectbox("Examples:", list(EXAMPLES.keys()))
if example_choice != "Select an example...":
    default_seq = EXAMPLES[example_choice]
else:
    default_seq = "Insert your protein sequence here"

txt = st.sidebar.text_area('Input Sequence', default_seq, height=200)

# Display sequence info
if txt and txt != "Insert your protein sequence here":
    clean_seq = re.sub(r'\s+', '', txt.upper())
    if clean_seq.startswith('>'):
        clean_seq = ''.join(clean_seq.split('\n')[1:])
    if clean_seq:
        st.sidebar.info(f"Sequence length: {len(clean_seq)} aa")

# ESMFold prediction function
def update(sequence=txt):
    # Validate sequence
    validated_seq, error = validate_sequence(sequence)
    
    if error and "Warning" not in error:
        st.error(error)
        return
    elif error:
        st.warning(error)
    
    if validated_seq is None:
        return
    
    max_attempts = 3
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for attempt in range(max_attempts):
        try:
            status_text.info(f"Attempting to contact ESMFold API... (Attempt {attempt + 1}/{max_attempts})")
            progress_bar.progress((attempt + 1) * 25)
            
            response = requests.post(
                'https://api.esmatlas.com/foldSequence/v1/pdb/',
                data=validated_seq,
                timeout=300
            )
            
            if response.status_code == 200:
                pdb_string = response.text
                
                if 'ATOM' in pdb_string and len(pdb_string) > 100:
                    progress_bar.progress(100)
                    status_text.success("Structure prediction successful!")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Save to session state
                    st.session_state.pdb_string = pdb_string
                    
                    with open('predicted.pdb', 'w') as f:
                        f.write(pdb_string)
                    
                    structure = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
                    
                    st.session_state.prediction_result = {
                        'structure': structure,
                        'pdb_string': pdb_string,
                        'sequence': validated_seq
                    }
                    return
                else:
                    st.warning(f"Invalid response from API (Attempt {attempt + 1})")
                    
            elif response.status_code == 400:
                st.error(f"Bad request: {response.text}")
                return
            elif response.status_code == 503:
                st.warning("Service temporarily unavailable...")
            else:
                st.warning(f"HTTP {response.status_code}: {response.text}")
            
            if attempt < max_attempts - 1:
                time.sleep(5)
            
        except requests.Timeout:
            status_text.warning(f"Request timed out (Attempt {attempt + 1})")
            if attempt < max_attempts - 1:
                time.sleep(5)
        except Exception as e:
            status_text.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(5)
    
    progress_bar.empty()
    status_text.error("ESMFold API is currently unavailable after multiple attempts.")

predict = st.sidebar.button('Predict', on_click=update, type="primary")

# Visualization options
if st.session_state.prediction_result is not None:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Visualization Options")
    color_scheme = st.sidebar.selectbox(
        "Color scheme:",
        ['spectrum', 'chain', 'secondary'],
        format_func=lambda x: {'spectrum': 'Spectrum (N→C)', 'chain': 'Chain', 'secondary': 'Secondary Structure'}[x]
    )
    spin_enabled = st.sidebar.checkbox("Enable rotation", value=True)

# File upload option
st.markdown("---")
st.subheader("Alternative: Upload a Pre-Computed PDB File")
st.info("If the API is down, you can generate structures using [ColabFold](https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb) and upload the PDB file here.")

uploaded_file = st.file_uploader("Upload PDB file", type=['pdb'])

if uploaded_file is not None:
    pdb_string = uploaded_file.read().decode('utf-8')
    
    with open('predicted.pdb', 'w') as f:
        f.write(pdb_string)
    
    structure = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
    
    st.session_state.prediction_result = {
        'structure': structure,
        'pdb_string': pdb_string,
        'sequence': None
    }
    st.session_state.pdb_string = pdb_string

# Display results
if st.session_state.prediction_result is not None:
    result = st.session_state.prediction_result
    structure = result['structure']
    pdb_string = result['pdb_string']
    
    b_value = round(structure.b_factor.mean(), 4)
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average pLDDT", f"{b_value}")
    with col2:
        if result['sequence']:
            st.metric("Sequence Length", f"{len(result['sequence'])} aa")
    with col3:
        confidence_label = "Very High" if b_value > 90 else "High" if b_value > 70 else "Low" if b_value > 50 else "Very Low"
        st.metric("Confidence", confidence_label)
    
    st.markdown("---")
    
    # Visualization
    st.subheader('3D Structure Visualization')
    color = color_scheme if 'color_scheme' in locals() else 'spectrum'
    spin = spin_enabled if 'spin_enabled' in locals() else True
    render_molecule(pdb_string, color, spin)
    
    st.markdown("---")
    
    # pLDDT information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader('pLDDT Score')
        st.write('pLDDT is a per-residue estimate of the confidence in prediction on a scale from 0-100.')
        st.info(f'**Average pLDDT: {b_value}**')
        
        st.write("**Confidence levels:**")
        st.write("Very High: > 90")
        st.write("High: 70-90")
        st.write("Low: 50-70")
        st.write("Very Low: < 50")
    
    with col2:
        st.subheader('Per-Residue Confidence')
        fig = plot_plddt_scores(structure)
        st.plotly_chart(fig, use_container_width=True)
    
    # Download button
    st.download_button(
        label="⬇️ Download PDB File",
        data=pdb_string,
        file_name='predicted.pdb',
        mime='text/plain',
        type="primary"
    )

elif not predict and uploaded_file is None:
    st.warning('Please either enter your protein sequence in the sidebar or use an example and click Predict or upload a PDB file!')
    
    # Help section
    with st.expander("How to use this app"):
        st.markdown("""
        **Step 1:** Enter your protein sequence in the sidebar
        - You can paste a sequence directly or try one of the example sequences
        - FASTA format is supported
        
        **Step 2:** Click the "Predict" button
        - The prediction may take 30 seconds to a few minutes
        - Longer sequences take more time
        
        **Step 3:** Explore your results
        - View the 3D structure
        - Check confidence scores
        - Download the PDB file
        
        **Alternative:** If the API is unavailable, you may upload a pre-computed PDB file from the AlphaFold Google Colab notebook.
        """)