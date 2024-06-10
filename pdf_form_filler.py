import fitz  # PyMuPDF
import cv2
import numpy as np  # Import NumPy


def fill_pdf_template(pdf_path, output_path, field_data):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)  # Load the first page of the PDF

    # Convert PDF page to an image (PNG)
    pix = page.get_pixmap()
    # Convert pixmap samples to a NumPy array
    img_array = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img_array.reshape(
        (pix.height, pix.width, pix.n)
    )  # Reshape the array to an image

    # Convert RGBA to BGR if needed
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    # img = cv2.imdecode(img_array, flags=cv2.IMREAD_COLOR)
    # if img is None:
    #     raise ValueError("Failed to decode image")

    # Overlay text/annotations onto the image
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_color = (0, 0, 255)  # BGR color format (here: red)
    text_size = 1
    text_thickness = 2
    text_positions = {
        "name": (100, 200),
        "age": (100, 250),
        "email": (100, 300)
        # Add more fields and corresponding positions as needed
    }

    for field, position in text_positions.items():
        cv2.putText(
            img,
            f"{field.capitalize()}: {field_data[field]}",
            position,
            font,
            text_size,
            text_color,
            text_thickness,
        )

    # Save the modified image
    cv2.imwrite(output_path, img)
    pdf_document.close()


# Path to your PDF file
pdf_file = "static/formularios_afiliacion/Formulario-Unico-de-AfiliacionAnexo-Formulario-PBS.pdf"

# User-specific data for filling the PDF form
user_data = {"name": "Fran", "age": "30", "email": "john@example.com"}

# Output path for the filled-out form image
output_image_path = "filled_form.png"

# Fill the PDF template and save the modified image
fill_pdf_template(pdf_file, output_image_path, user_data)

# Now 'filled_form.png' contains the modified image with filled-out form fields
