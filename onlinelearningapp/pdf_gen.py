import os

import pdfkit

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
path_to_wkhtmltopdf = os.getcwd() + os.sep + '../wkhtmltox/bin/wkhtmltopdf.exe'


def generate_pdf(studentName, dateStr, instructorName, pdfFilePath):
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Course Completion Certificate</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }
            .certificate {
                max-width: 800px;
                margin: 0 auto;
                padding: 30px;
                border: 2px solid #333;
            }
            .certificate-title {
                font-size: 24px;
                font-weight: bold;
                text-align: center;
            }
            .certificate-content {
                font-size: 18px;
                margin-top: 20px;
                text-align: center;
            }
            .student-name {
                font-size: 22px;
                font-weight: bold;
                margin-top: 40px;
                text-align: center;
            }
            .course-name {
                font-size: 20px;
                margin-top: 20px;
                text-align: center;
            }
            .completion-date {
                font-size: 18px;
                margin-top: 20px;
                text-align: center;
            }
            .signature {
                font-size: 18px;
                font-weight: bold;
                margin-top: 40px;
                text-align: center;
            }
            .instructor-name {
                font-size: 18px;
                margin-top: 10px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="certificate">
            <div class="certificate-title">Certificate of Completion</div>
            <div class="certificate-content">This is to certify that</div>
            <div class="student-name">[Student Name]</div>
            <div class="course-name">has successfully completed the course</div>
            <div class="completion-date">on [Completion Date]</div>
            <div class="signature">Authorized Signature</div>
            <div class="instructor-name">[Instructor Name]</div>
        </div>
    </body>
    </html>
    '''
    html = html.replace("[Student Name]", studentName).replace("[Completion Date]", dateStr).replace(
        "[Instructor Name]", instructorName)
    try:
        pdfkit.from_string(html, pdfFilePath, configuration=pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf))
    except Exception as e:
        print(e)
        return False
    return True

# generate_pdf('Azhar Syed', 'July 21, 2023', 'Dr. Azanm Yacoub', 'azhar_syed_course1.pdf')
