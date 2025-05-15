import streamlit as st
from PIL import Image, ImageDraw
from streamlit_cropper import st_cropper
import base64
import io
from jinja2 import Template

# Set wide layout
# st.set_page_config(page_title="Email Signature Generator", layout="wide")

# Load selected template
def load_template(option):
    if option == "Welsford":
        file = "templates/welsford_signature.html"
    elif option == "Valveman":
        file = "templates/valveman_signature.html"
    else:  # "Both"
        file = "templates/both_signature.html"
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

# Convert image to base64
def encode_image(img: Image.Image):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

# Format number to tel:+ format
def format_tel(number):
    return "+{}".format("".join(filter(str.isdigit, number)))

# Title
st.title("📧 Email Signature Generator")

# Step 1: Upload photo first
if "image_uploaded" not in st.session_state:
    st.session_state.image_uploaded = None

uploaded_file = st.file_uploader("Upload Profile Photo", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.session_state.image_uploaded = uploaded_file

cropped_img = None
encoded_image = None

if st.session_state.image_uploaded:
    st.subheader("🖼️ Crop & Zoom (Optional)")
    image = Image.open(st.session_state.image_uploaded).convert("RGBA")

    # Fill transparent background with white
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    image = Image.alpha_composite(background, image)

    cropped_img = st_cropper(image, box_color='blue', aspect_ratio=(1, 1))

    # Make it circular
    mask = Image.new("L", cropped_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, cropped_img.size[0], cropped_img.size[1]), fill=255)
    cropped_img.putalpha(mask)

    encoded_image = encode_image(cropped_img)

# Step 2: User Form
st.subheader("✍️ Signature Details")

with st.form("signature_form"):
    signature_type = st.selectbox("Choose Signature Type", ["Welsford", "Valveman", "Both"])

    first_name = st.text_input("First Name", value="")
    last_name = st.text_input("Last Name", value="")
    title = st.text_input("Job Title", value="")

    phone_display = st.text_input("Personal Phone Number", value="610-420-0888")
    office_display = st.text_input("Office Phone Number", value="888-825-8800")

    website_choice = st.radio("Websites to show", ["Both", "Welsford only", "Valveman only"])

    submit = st.form_submit_button("Generate Signature")

# Step 3: Generate HTML
if submit and encoded_image:
    template_str = load_template(signature_type)
    template = Template(template_str)

    phone_link = format_tel(phone_display)
    office_link = format_tel(office_display)

    show_personal = bool(phone_display.strip())
    show_office = bool(office_display.strip())

    html_output = template.render(
        first_name=first_name,
        last_name=last_name,
        title=title,
        photo_url=encoded_image,
        phone_display=phone_display,
        phone_link=phone_link,
        office_display=office_display,
        office_link=office_link,
        show_personal=show_personal,
        show_office=show_office,
        show_welsford=(website_choice in ["Both", "Welsford only"]),
        show_valveman=(website_choice in ["Both", "Valveman only"]),
    )

    st.subheader("🔎 Preview")
    st.components.v1.html(html_output, height=450, scrolling=True)

    # Download filename
    if signature_type == "Welsford":
        filename = f"welsford_{first_name.lower()}_{last_name.lower()}_signature.html"
    elif signature_type == "Valveman":
        filename = f"valveman_{first_name.lower()}_{last_name.lower()}_signature.html"
    else:
        filename = f"{first_name.lower()}_{last_name.lower()}_signature.html"

    b64 = base64.b64encode(html_output.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}">📥 Download Signature HTML</a>'
    st.markdown(href, unsafe_allow_html=True)
elif submit and not encoded_image:
    st.error("⚠️ Please upload and crop a profile photo before generating the signature.")