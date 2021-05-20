import os
import os.path
import pathlib
import subprocess
import sys
import glob


def fmp_dump(data, input_file_name, output, adr_field_map):
    from xml.etree.ElementTree import TreeBuilder, tostring
    import ptulsconv

    doc = TreeBuilder(element_factory=None)

    doc.start('FMPXMLRESULT', {'xmlns': 'http://www.filemaker.com/fmpxmlresult'})

    doc.start('ERRORCODE', {})
    doc.data('0')
    doc.end('ERRORCODE')

    doc.start('PRODUCT', {'NAME': ptulsconv.__name__, 'VERSION': ptulsconv.__version__})
    doc.end('PRODUCT')

    doc.start('DATABASE', {'DATEFORMAT': 'MM/dd/yy', 'LAYOUT': 'summary', 'TIMEFORMAT': 'hh:mm:ss',
                           'RECORDS': str(len(data['events'])), 'NAME': os.path.basename(input_file_name)})
    doc.end('DATABASE')

    doc.start('METADATA', {})
    for field in adr_field_map:
        tp = field[2]
        ft = 'TEXT'
        if tp is int or tp is float:
            ft = 'NUMBER'

        doc.start('FIELD', {'EMPTYOK': 'YES', 'MAXREPEAT': '1', 'NAME': field[1], 'TYPE': ft})
        doc.end('FIELD')
    doc.end('METADATA')

    doc.start('RESULTSET', {'FOUND': str(len(data['events']))})
    for event in data['events']:
        doc.start('ROW', {})
        for field in adr_field_map:
            doc.start('COL', {})
            doc.start('DATA', {})
            for key_attempt in field[0]:
                if key_attempt in event.keys():
                    doc.data(str(event[key_attempt]))
                    break
            doc.end('DATA')
            doc.end('COL')
        doc.end('ROW')
    doc.end('RESULTSET')

    doc.end('FMPXMLRESULT')
    docelem = doc.close()
    xmlstr = tostring(docelem, encoding='unicode', method='xml')
    output.write(xmlstr)

xslt_path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'xslt')


def xform_options():
    return glob.glob(os.path.join(xslt_path, "*.xsl"))


def dump_xform_options(output=sys.stdout):
    print("# Available transforms:", file=output)
    print("# Transform dir: %s" % xslt_path, file=output)
    for f in xform_options():
        base = os.path.basename(f)
        name, _ = os.path.splitext(base)
        print("#    " + name, file=output)


def fmp_transformed_dump(data, input_file, xsl_name, output, adr_field_map):
    from ptulsconv.reporting import print_status_style
    import io

    pipe = io.StringIO()

    print_status_style("Generating base XML")
    fmp_dump(data, input_file, pipe, adr_field_map)

    str_data = pipe.getvalue()
    print_status_style("Base XML size %i" % (len(str_data)))

    print_status_style("Running xsltproc")

    xsl_path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'xslt', xsl_name + ".xsl")
    print_status_style("Using xsl: %s" % xsl_path)
    subprocess.run(['xsltproc', xsl_path, '-'],
                   input=str_data, text=True,
                   stdout=output, shell=False, check=True)
