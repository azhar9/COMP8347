import pdfkit

config = pdfkit.configuration(wkhtmltopdf='../wkhtmltox/bin/')

# HTML content as a string
html_string = '''
<html>
<head>
    <title>PDF from String</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This PDF was generated from a string of HTML content.</p>
</body>
</html>
'''

# Generate PDF from the HTML string
pdfkit.from_string(html_string, 'output.pdf')
