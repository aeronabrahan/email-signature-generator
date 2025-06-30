import os
import io
import base64
import streamlit as st
from jinja2 import Template
from PIL import Image, ImageDraw
from streamlit_cropper import st_cropper

# Set wide layout
st.set_page_config(page_title="Email Signature Generator", layout="wide")

# Load selected template
def load_template(option):
    file = {
        "Welsford": "templates/welsford_signature.html",
        "Valveman": "templates/valveman_signature.html",
        "Both": "templates/both_signature.html"
    }[option]
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

# Format number to tel:+ format
def format_tel(number):
    return "+{}".format("".join(filter(str.isdigit, number)))

# Convert and compress image to base64

def encode_image(img: Image.Image):
    buffered = io.BytesIO()
    img.convert("RGBA").save(buffered, format="PNG")  # No resize, no compression
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

# def encode_image(img: Image.Image):
#     buffered = io.BytesIO()
#     img.convert("RGBA").save(buffered, format="PNG")

#     image_data = buffered.getvalue()
#     if len(image_data) > 2 * 1024 * 1024:  # 2MB limit
#         return None

#     return "data:image/png;base64," + base64.b64encode(image_data).decode()

# def encode_image(img: Image.Image):
#     # Resize to smaller square (e.g., 96x96 or 80x80)
#     resized = img.resize((96, 96))
    
#     # Convert to JPEG for much smaller size
#     rgb_img = resized.convert("RGB")
#     buffered = io.BytesIO()
#     rgb_img.save(buffered, format="JPEG", quality=70)  # Lower quality if needed

#     image_data = buffered.getvalue()
#     # Optional: limit size check
#     if len(image_data) > 100 * 1024:  # 100 KB limit
#         return None

#     return "data:image/jpeg;base64," + base64.b64encode(image_data).decode()

# Title
st.title("\U0001F4E7 Email Signature Generator")

# Step 1: Upload photo
st.subheader("\U0001F5BC️ Step 1: Upload and Crop Profile Photo")
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
uploaded_file = st.file_uploader("Upload Profile Photo", type=["png", "jpg", "jpeg"])
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file

cropped_img = None
encoded_image = None

# if st.session_state.uploaded_file:
#     image = Image.open(st.session_state.uploaded_file).convert("RGBA")
#     cropped_img = st_cropper(image, box_color='blue', aspect_ratio=(1, 1))

#     # Fill transparent background with white
#     background = Image.new("RGBA", cropped_img.size, (255, 255, 255, 255))
#     cropped_img = Image.alpha_composite(background, cropped_img)

#     # Make it circular
#     mask = Image.new("L", cropped_img.size, 0)
#     draw = ImageDraw.Draw(mask)
#     draw.ellipse((0, 0, cropped_img.size[0], cropped_img.size[1]), fill=255)
#     cropped_img.putalpha(mask)

#     encoded_image = encode_image(cropped_img)
#     st.image(cropped_img, caption="Cropped Image Preview", width=120)

if st.session_state.uploaded_file:
    image = Image.open(st.session_state.uploaded_file).convert("RGBA")
    cropped_img = st_cropper(image, box_color='blue', aspect_ratio=(1, 1))

    # Fill transparent background with white
    background = Image.new("RGBA", cropped_img.size, (255, 255, 255, 255))
    cropped_img = Image.alpha_composite(background, cropped_img)

    # Make it circular
    mask = Image.new("L", cropped_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, cropped_img.size[0], cropped_img.size[1]), fill=255)
    cropped_img.putalpha(mask)

    encoded_image = encode_image(cropped_img)

    if encoded_image:
        st.image(cropped_img, caption="Cropped Image Preview", width=120)
    else:
        st.error("The final image exceeds the 2MB limit. Please crop or upload a smaller image.")

# Step 2: Signature form
st.subheader("\u270D\ufe0f Step 2: Signature Details")
# include_photo = st.checkbox("Include Profile Photo", value=True)

with st.form("signature_form"):
    signature_type = st.selectbox("Choose Signature Type", ["Welsford", "Valveman", "Both"])
    first_name = st.text_input("First Name", value="")
    last_name = st.text_input("Last Name", value="")
    title = st.text_input("Job Title", value="")
    phone_display = st.text_input("Personal Phone Number", value="610-420-0888")
    office_display = st.text_input("Office Phone Number", value="888-825-8800")
    website_choice = st.radio("Websites to show", ["Both", "Welsford only", "Valveman only"])
    submit = st.form_submit_button("Generate Signature")

# Step 3: Render signature
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
        # photo_url=encoded_image if include_photo else "",
        phone_display=phone_display,
        phone_link=phone_link,
        office_display=office_display,
        office_link=office_link,
        show_personal=show_personal,
        show_office=show_office,
        show_welsford=(website_choice in ["Both", "Welsford only"]),
        show_valveman=(website_choice in ["Both", "Valveman only"]),
    )

    st.subheader("\U0001F50E Preview")
    st.components.v1.html(html_output, height=500, scrolling=True)

    filename = f"{signature_type.lower()}_{first_name.lower()}_{last_name.lower()}_signature.html"
    st.download_button("\U0001F4E5 Download Signature HTML", html_output, file_name=filename, mime="text/html")
elif submit:
    st.error("\u26A0\ufe0f Please upload and crop a profile photo before generating the signature.")
