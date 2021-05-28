import io
from IPython.display import display, IFrame
from fpdf import FPDF
from PyPDF2 import PdfFileReader, PdfFileWriter


font_size = 10
max_text_width = 150
extraction_box_color = (102, 255, 178)
extracted_values_color = (165, 42, 42)


def create_overlay(extraction_result, document_path, output_path):
    input_pdf = PdfFileReader(document_path)
    output_pdf = PdfFileWriter()

    pdf = FPDF(unit='pt')
    pdf.set_font('Helvetica')
    pdf.set_font_size(font_size)
    pdf.set_margins(0, 0)
    pdf.set_line_width(1)

    for n in range(len(input_pdf.pages)):
        input_page = input_pdf.getPage(n)
        width = float(input_page.mediaBox.getWidth())
        height = float(input_page.mediaBox.getHeight())
        pdf.add_page(format=(width, height))

        # add legend
        pdf.set_fill_color(*extraction_box_color)
        pdf.rect(0.8 * width, 5, 10, 5, style='F')
        pdf.set_xy(0.8 * width + 10, 7)
        pdf.cell(0, txt='Extraction area', ln=1)

        pdf.set_fill_color(*extracted_values_color)
        pdf.rect(0.8 * width, 15, 10, 5, style='F')
        pdf.set_xy(0.8 * width + 10, 18)
        pdf.cell(0, txt='Extracted values')

        for hf in (hf for hf in extraction_result['extraction']['headerFields'] if hf['page'] == n + 1):
            x = hf['coordinates']['x']
            y = hf['coordinates']['y']
            w = hf['coordinates']['w']
            h = hf['coordinates']['h']
            # draw box around the area of the prediction
            pdf.set_draw_color(*extraction_box_color)
            pdf.rect(x * width, y * height, w * width, h * height)

            # draw the extracted value
            pdf.set_draw_color(*extracted_values_color)
            pdf.set_xy((x + w) * width + 2, y * height)
            pdf.multi_cell(min(pdf.get_string_width(str(hf['value'])) + 6, max_text_width), h=font_size,
                           txt=str(hf['value']), border=1)

        for li in (li for line in extraction_result['extraction']['lineItems'] for li in line if li['page'] == n + 1):
            x = li['coordinates']['x']
            y = li['coordinates']['y']
            w = li['coordinates']['w']
            h = li['coordinates']['h']
            # draw box around the area of the prediction
            pdf.set_draw_color(*extraction_box_color)
            pdf.rect(x * width, y * height, w * width, h * height)

            # draw the extracted value
            pdf.set_draw_color(*extracted_values_color)
            pdf.set_xy((x + w) * width, y * height)
            pdf.multi_cell(min(pdf.get_string_width(str(li['value'])) + 6, max_text_width), h=font_size,
                           txt=str(li['value']), border=1)

    overlay = PdfFileReader(io.BytesIO(pdf.output()))

    for n in range(len(input_pdf.pages)):
        page = input_pdf.getPage(n)
        page.mergePage(overlay.getPage(n))
        output_pdf.addPage(page)

    with open(output_path, 'wb') as out:
        output_pdf.write(out)


def display_extraction(extraction_result, input_document):
    output_path = f"extraction_{extraction_result['id']}.pdf"
    create_overlay(extraction_result, input_document, output_path)
    display(IFrame(output_path, 700, 1000))


def display_capabilities(capabilities):
    document_types = capabilities['documentTypes']
    print('Available document types:', document_types)
    print('Available extraction fields:')
    for document_type in document_types:
        print(f"for '{document_type}':")
        print('\tHeader fields:')
        [print('\t\t', hf['name']) for hf in capabilities['extraction']['headerFields'] if
         (document_type in hf['supportedDocumentTypes'])]
        print('\tLine item fields:')
        [print('\t\t', li['name']) for li in capabilities['extraction']['lineItemFields'] if
         (document_type in li['supportedDocumentTypes'])]
