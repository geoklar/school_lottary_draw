import random
from datetime import datetime
from flask import Flask, render_template, send_file, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io

# Initialize Flask app
app = Flask(__name__)

# Read gifts from the file
gifts = []
with open("gifts.txt", "r", encoding="utf-8") as file:
    gifts = [line.strip() for line in file]

# Add a date for the raffle
current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
current_pdf_date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

# Generate unique numbers for the gifts
unique_numbers = random.sample(range(1, 3001), len(gifts))
gift_allocation = dict(zip(unique_numbers, gifts))

# Register a font for PDF generation
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans-Bold.ttf'))


# Helper function to generate the PDF
def generate_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont('DejaVuSans', 10)

    y = 750
    page_number = 1

    def draw_header_footer():
        pdf.drawString(30, 820, f"Κλήρωση Δώρων - Ημερομηνία: {current_date}")
        pdf.drawString(500, 820, f"Σελίδα: {page_number}")
        pdf.drawString(30, 20, f"Ημερομηνία: {current_date}")
        pdf.drawString(500, 20, f"Σελίδα: {page_number}")

    draw_header_footer()

    for number, gift in gift_allocation.items():
        pdf.drawString(100, y, f"🎁 Δώρο '{gift}': Λαχνός {number}")
        y -= 20

        if y < 50:  # If no more space on the page
            pdf.showPage()
            page_number += 1
            y = 750
            pdf.setFont('DejaVuSans', 10)
            draw_header_footer()

    pdf.save()
    buffer.seek(0)
    return buffer


@app.route('/')
def home():
    return render_template('index.html')  # Ensure you have an index.html in your templates folder


@app.route('/api/start_raffle', methods=['GET'])
def start_raffle():
    # Generate results dynamically for the UI
    results = [{"gift": gift, "ticket": number} for number, gift in gift_allocation.items()]
    return jsonify(results)


@app.route('/download', methods=['GET'])
def download():
    pdf_buffer = generate_pdf()
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Αποτελέσματα_κλήρωσης_{current_pdf_date}.pdf",
        mimetype="application/pdf",
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443)
