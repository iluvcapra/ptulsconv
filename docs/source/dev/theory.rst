Theory of Operation
===================

Execution Flow When Producing "doc" Output
------------------------------------------

#. The command line argv is read in `__main__.main()`, 
   which calls `commands.convert()`
#. `commands.convert()` reads the input with `docparser.doc_parser_visitor()`,
   which uses the `parsimonious` library to parse the input into an abstract
   syntax tree, which the parser visitor uses to convert into a 
   `docparser.doc_entity.SessionDescriptor`, which structures all of the data
   in the session output.
#. The next action based on the output format. In the 
   case of the "doc" output format, it runs some validations
   on the input, and calls `commands.generate_documents()`.
#. `commands.generate_documents()` creates the output folder, creates the
   Continuity report with `pdf.continuity.output_continuity()` (this document 
   requires some special-casing), and at the tail calls...
#. `commands.create_adr_reports()`, which creates folders for 

(FIXME finish this)