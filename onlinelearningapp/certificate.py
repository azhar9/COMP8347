import os
import pdfkit
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
import urllib.request
from urllib.parse import urljoin

class PdfGen:
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        "enable-local-file-access": "",
        "zoom": "1",
        "load-error-handling": "ignore",
        "load-media-error-handling": "ignore",
        "javascript-delay": "1000",
        "log-level": "error"
    }
    path_to_wkhtmltopdf = os.getcwd() + os.sep + '/wkhtmltox/bin/wkhtmltopdf.exe'

    @staticmethod
    def generate_pdf(studentName, dateStr, instructorName, courseName, pdfFilePath):
        script_dir = os.path.dirname(__file__)  # Get the directory of the current script
        template_path = os.path.join(script_dir, 'templates', 'certificate_template.html')  # Create the path to the template

        # Get the absolute path to the first image file
        image_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'Eduhub-4 2.png')
        image_path = os.path.abspath(image_path)
        image_url = urljoin('file:', urllib.request.pathname2url(image_path)) # Convert the image path to a file URI

        # Get the absolute path to the second image file
        stamp_image_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'CertificateStamp.png')
        stamp_image_path = os.path.abspath(stamp_image_path)
        stamp_image_url = urljoin('file:', urllib.request.pathname2url(stamp_image_path)) # Convert the image path to a file URI

        with open(template_path, 'r') as file:
            html = file.read()

        html = f"{html}"  # convert the HTML to a formatted string
        html = html.replace('{studentName}', studentName).replace('{dateStr}', dateStr).replace('{instructorName}',
                                                                                                instructorName).replace(
            '{courseName}', courseName).replace('{imageUrl}', image_url).replace('{stampUrl}', stamp_image_url)

        try:
            pdfkit.from_string(html, pdfFilePath, options=PdfGen.options,
                               configuration=pdfkit.configuration(wkhtmltopdf=PdfGen.path_to_wkhtmltopdf))
        except Exception as e:
            print(e)
            return False
        return True
