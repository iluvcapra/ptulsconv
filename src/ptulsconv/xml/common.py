from __future__ import annotations

import glob
import os
import os.path
import pathlib
import subprocess
import sys
from datetime import datetime
from importlib.metadata import version as module_version
from xml.etree.ElementTree import TreeBuilder, tostring

import ptulsconv
from ptulsconv.docparser.adr_entity import ADRLine

# TODO Get a third-party test for Avid Marker lists


def avid_marker_list(
    lines: list[ADRLine],
    report_date: datetime | None = None,
    reel_start_frame=0,
    fps=24,
):
    doc = TreeBuilder(element_factory=None)

    if report_date is None:
        report_date = datetime.now()

    doc.start("Avid:StreamItems", {"xmlns:Avid": "http://www.avid.com"})
    doc.start("Avid:XMLFileData", {})
    doc.start("AvProp", {"name": "DomainMagic", "type": "string"})
    doc.data("Domain")
    doc.end("AvProp")
    doc.start("AvProp", {"name": "DomainKey", "type": "string"})
    doc.data("58424a44")
    doc.end("AvProp")

    def insert_elem(kind, attb, atype, name, value):
        doc.start("ListElem", {})
        doc.start("AvProp", {"id": "ATTR", "name": "OMFI:ATTB:Kind", "type": "int32"})
        doc.data(kind)
        doc.end("AvProp")

        doc.start("AvProp", {"id": "ATTR", "name": "OMFI:ATTB:Name", "type": "string"})
        doc.data(name)
        doc.end("AvProp")

        doc.start("AvProp", {"id": "ATTR", "name": attb, "type": atype})
        doc.data(value)
        doc.end("AvProp")

        doc.end("ListElem")

    for line in lines:
        doc.start("AvClass", {"id": "ATTR"})
        doc.start(
            "AvProp", {"id": "ATTR", "name": "__OMFI:ATTR:NumItems", "type": "int32"}
        )
        doc.data("7")
        doc.end("AvProp")

        doc.start("List", {"id": "OMFI:ATTR:AttrRefs"})

        assert report_date

        insert_elem(
            "1",
            "OMFI:ATTB:IntAttribute",
            "int32",
            "_ATN_CRM_LONG_CREATE_DATE",
            report_date.strftime("%s"),
        )
        insert_elem(
            "2", "OMFI:ATTB:StringAttribute", "string", "_ATN_CRM_COLOR", "yellow"
        )
        insert_elem(
            "2",
            "OMFI:ATTB:StringAttribute",
            "string",
            "_ATN_CRM_USER",
            line.supervisor or "",
        )

        marker_name = f"{line.cue_number}: {line.prompt}"
        insert_elem(
            "2", "OMFI:ATTB:StringAttribute", "string", "_ATN_CRM_COM", marker_name
        )

        start_frame = int(line.start * fps)

        insert_elem(
            "2",
            "OMFI:ATTB:StringAttribute",
            "string",
            "_ATN_CRM_TC",
            str(start_frame - reel_start_frame),
        )

        insert_elem("2", "OMFI:ATTB:StringAttribute", "string", "_ATN_CRM_TRK", "V1")
        insert_elem("1", "OMFI:ATTB:IntAttribute", "int32", "_ATN_CRM_LENGTH", "1")

        doc.start("ListElem", {})
        doc.end("ListElem")

        doc.end("List")
        doc.end("AvClass")

    doc.end("Avid:XMLFileData")
    doc.end("Avid:StreamItems")


def dump_fmpxml(data, input_file_name, output, adr_field_map):
    doc = TreeBuilder(element_factory=None)

    doc.start("FMPXMLRESULT", {"xmlns": "http://www.filemaker.com/fmpxmlresult"})

    doc.start("ERRORCODE", {})
    doc.data("0")
    doc.end("ERRORCODE")

    version = module_version("ptulsconv")
    doc.start("PRODUCT", {"NAME": ptulsconv.__name__, "VERSION": f"{version}"})
    doc.end("PRODUCT")

    doc.start(
        "DATABASE",
        {
            "DATEFORMAT": "MM/dd/yy",
            "LAYOUT": "summary",
            "TIMEFORMAT": "hh:mm:ss",
            "RECORDS": str(len(data["events"])),
            "NAME": os.path.basename(input_file_name),
        },
    )
    doc.end("DATABASE")

    doc.start("METADATA", {})
    for field in adr_field_map:
        tp = field[2]
        ft = "TEXT"
        if tp is int or tp is float:
            ft = "NUMBER"

        doc.start(
            "FIELD", {"EMPTYOK": "YES", "MAXREPEAT": "1", "NAME": field[1], "TYPE": ft}
        )
        doc.end("FIELD")
    doc.end("METADATA")

    doc.start("RESULTSET", {"FOUND": str(len(data["events"]))})
    for event in data["events"]:
        doc.start("ROW", {})
        for field in adr_field_map:
            doc.start("COL", {})
            doc.start("DATA", {})
            for key_attempt in field[0]:
                if key_attempt in event:
                    doc.data(str(event[key_attempt]))
                    break
            doc.end("DATA")
            doc.end("COL")
        doc.end("ROW")
    doc.end("RESULTSET")

    doc.end("FMPXMLRESULT")
    docelem = doc.close()
    xmlstr = tostring(docelem, encoding="unicode", method="xml")
    output.write(xmlstr)


xslt_path = os.path.join(pathlib.Path(__file__).parent.absolute(), "xslt")


def xform_options():
    return glob.glob(os.path.join(xslt_path, "*.xsl"))


def dump_xform_options(output=sys.stdout):
    print("# Available transforms:", file=output)
    print(f"# Transform dir: {xslt_path}", file=output)
    for f in xform_options():
        base = os.path.basename(f)
        name, _ = os.path.splitext(base)
        print("#    " + name, file=output)


def fmp_transformed_dump(data, input_file, xsl_name, output, adr_field_map):
    import io

    from ptulsconv.reporting import print_status_style

    pipe = io.StringIO()

    print_status_style("Generating base XML")
    dump_fmpxml(data, input_file, pipe, adr_field_map)

    str_data = pipe.getvalue()
    print_status_style(f"Base XML size {len(str_data)}")

    print_status_style("Running xsltproc")

    xsl_path = os.path.join(
        pathlib.Path(__file__).parent.absolute(), "xslt", xsl_name + ".xsl"
    )
    print_status_style(f"Using xsl: {xsl_path}")
    subprocess.run(
        ["xsltproc", xsl_path, "-"],
        input=str_data,
        text=True,
        stdout=output,
        shell=False,
        check=True,
    )
