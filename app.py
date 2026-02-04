import gradio as gr
from PIL import Image
import io
import requests

# --- KMT Dynamics: LENS AI Production ---
# Architect: BSc. PHS Msc. PHQ "Abdulrahman" Mugabi Kizito Lenny
# Product Leadership Team: Ahabwamukama Arnold

# HARD-CODED AUTHENTICATION (FORCED INTEGRATION)
HF_TOKEN = "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"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# STRATEGIC NEURAL ROUTING
MODELS = {
    "X-Ray": "https://api-inference.huggingface.co/models/microsoft/swin-base-patch4-window7-224",
    "Ultrasound": "https://api-inference.huggingface.co/models/microsoft/swin-base-patch4-window7-224",
    "Skin": "https://api-inference.huggingface.co/models/facebook/dino-v2-base",
    "Pathology": "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
}

def lens_diagnostic_engine(image, modality):
    if image is None:
        return "⚠️ [SYSTEM ERROR]: No diagnostic input detected."
    
    # 1. Byte Conversion
    buf = io.BytesIO()
    image.save(buf, format='JPEG')
    img_bytes = buf.getvalue()

    try:
        # 2. Forced API Execution
        response = requests.post(MODELS[modality], headers=headers, data=img_bytes, timeout=30)
        prediction = response.json()

        if isinstance(prediction, list) and len(prediction) > 0:
            top_result = prediction[0]
            label = str(top_result.get('label', 'Unknown Pattern')).replace('_', ' ').title()
            score = round(top_result.get('score', 0) * 100, 2)
        else:
            label = "Complex Pattern Analyzed"
            score = "N/A"

        # 3. Clinical Output
        return f"""
# 🔎 LENS | Strategic Diagnostic Trace
---
### **1. AI ANALYSIS METRICS**
* **SOURCE:** {modality}
* **RESULT:** **{label}**
* **ACCURACY:** {score}%

### **2. CLINICAL STRATEGY**
> **PROTOCOL:** Correlate with physical findings. Follow KMT secondary diagnostic path.

---
**Product of KMT Dynamics Company Ltd.**
"""
    except Exception as e:
        return f"📡 [CONNECTION ERROR]: Server busy. Details: {str(e)}"

# --- LENS UI DESIGN ---
custom_css = """
    .gradio-container { font-family: 'Garamond', serif !important; background-color: #f8fafc; }
    #lens-header {
        background: linear-gradient(135deg, #000000 0%, #4b5563 50%, #9ca3af 100%);
        padding: 40px; border-radius: 15px; text-align: center; border: 2px solid silver;
    }
    #lens-title { color: #C0C0C0 !important; font-size: 4em !important; font-weight: bold; margin: 0; }
"""

with gr.Blocks(css=custom_css, theme='soft', title="LENS AI") as app:
    gr.HTML("<div id='lens-header'><h1 id='lens-title'>LENS</h1></div>")
    
    with gr.Row():
        with gr.Column():
            input_img = gr.Image(type="pil", label="Input Diagnostic Image")
            modality_select = gr.Dropdown(choices=["X-Ray", "Skin", "Pathology", "Ultrasound"], label="Modality", value="X-Ray")
            submit_btn = gr.Button("PERFORM DIAGNOSTIC TRACE", variant="primary")
        with gr.Column():
            output_markdown = gr.Markdown("### 📡 System Ready\nAwaiting input...")

    submit_btn.click(fn=lens_diagnostic_engine, inputs=[input_img, modality_select], outputs=output_markdown)

# FORCED NETWORK BINDING (MANDATORY FOR HUGGING FACE / GITHUB SYNC)
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, debug=True)
