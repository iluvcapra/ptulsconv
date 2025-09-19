import os
import os.path
import pathlib
import subprocess
import sys
import glob
import datetime
from xml.etree.ElementTree import TreeBuilder, tostring
from typing import List

import ptulsconv
from ptulsconv.docparser.adr_entity import ADRLine

# TODO Get a third-party test for Avid Marker lists


def avid_marker_list(lines: List[ADRLine], report_date=datetime.datetime.now(),
                     reel_start_frame=0, fps=24):
    doc = TreeBuilder(element_factory=None)

    doc.start('Avid:StreamItems', {'xmlns:Avid': 'http://www.avid.com'})
    doc.start('Avid:XMLFileData', {})
    doc.start('AvProp', {'name': 'DomainMagic', 'type': 'string'})
    doc.data("Domain")
    doc.end('AvProp')
    doc.start('AvProp', {'name': 'DomainKey', 'type': 'string'})
    doc.data("58424a44")
    doc.end('AvProp')

    def insert_elem(kind, attb, atype, name, value):
        doc.start('ListElem', {})
        doc.start('AvProp', {'id': 'ATTR',
                             'name': 'OMFI:ATTB:Kind',
                             'type': 'int32'})
        doc.data(kind)
        doc.end('AvProp')

        doc.start('AvProp', {'id': 'ATTR',
                             'name': 'OMFI:ATTB:Name',
                             'type': 'string'})
        doc.data(name)
        doc.end('AvProp')

        doc.start('AvProp', {'id': 'ATTR',
                             'name': attb,
                             'type': atype})
        doc.data(value)
        doc.end('AvProp')

        doc.end('ListElem')

    for line in lines:
        doc.start('AvClass', {'id': 'ATTR'})
        doc.start('AvProp', {'id': 'ATTR',
                             'name': '__OMFI:ATTR:NumItems',
                             'type': 'int32'})
        doc.data('7')
        doc.end('AvProp')

        doc.start('List', {'id': 'OMFI:ATTR:AttrRefs'})

        insert_elem('1', 'OMFI:ATTB:IntAttribute', 'int32',
                    '_ATN_CRM_LONG_CREATE_DATE', report_date.strftime("%s"))
        insert_elem('2', 'OMFI:ATTB:StringAttribute', 'string',
                    '_ATN_CRM_COLOR', 'yellow')
        insert_elem('2', 'OMFI:ATTB:StringAttribute', 'string',
                    '_ATN_CRM_USER', line.supervisor or "")

        marker_name = "%s: %s" % (line.cue_number, line.prompt)
        insert_elem('2', 'OMFI:ATTB:StringAttribute', 'string',
                    '_ATN_CRM_COM', marker_name)

        start_frame = int(line.start * fps)

        insert_elem('2', "OMFI:ATTB:StringAttribute", 'string',
                    '_ATN_CRM_TC',
                    str(start_frame - reel_start_frame))

        insert_elem('2', "OMFI:ATTB:StringAttribute", 'string',
                    '_ATN_CRM_TRK', 'V1')
        insert_elem('1', "OMFI:ATTB:IntAttribute", 'int32',
                    '_ATN_CRM_LENGTH', '1')

        doc.start('ListElem', {})
        doc.end('ListElem')

        doc.end('List')
        doc.end('AvClass')

    doc.end('Avid:XMLFileData')
    doc.end('Avid:StreamItems')


def dump_fmpxml(data, input_file_name, output, adr_field_map):
    doc = TreeBuilder(element_factory=None)

    doc.start('FMPXMLRESULT', {'xmlns':
                               'http://www.filemaker.com/fmpxmlresult'})

    doc.start('ERRORCODE', {})
    doc.data('0')
    doc.end('ERRORCODE')

    doc.start('PRODUCT', {'NAME': ptulsconv.__name__,
                          'VERSION': ptulsconv.__version__})
    doc.end('PRODUCT')

    doc.start('DATABASE', {'DATEFORMAT': 'MM/dd/yy',
                           'LAYOUT': 'summary',
                           'TIMEFORMAT': 'hh:mm:ss',
                           'RECORDS': str(len(data['events'])),
                           'NAME': os.path.basename(input_file_name)})
    doc.end('DATABASE')

    doc.start('METADATA', {})
    for field in adr_field_map:
        tp = field[2]
        ft = 'TEXT'
        if tp is int or tp is float:
            ft = 'NUMBER'

        doc.start('FIELD', {'EMPTYOK': 'YES', 'MAXREPEAT': '1',
                            'NAME': field[1], 'TYPE': ft})
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
    dump_fmpxml(data, input_file, pipe, adr_field_map)

    str_data = pipe.getvalue()
    print_status_style("Base XML size %i" % (len(str_data)))

    print_status_style("Running xsltproc")

    xsl_path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'xslt',
                            xsl_name + ".xsl")
    print_status_style("Using xsl: %s" % xsl_path)
    subprocess.run(['xsltproc', xsl_path, '-'],
                   input=str_data, text=True,
                   stdout=output, shell=False, check=True)
