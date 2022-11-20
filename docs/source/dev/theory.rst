Theory of Operation
===================

Execution Flow When Producing "doc" Output
------------------------------------------

#. The command line argv is read in :py:func:`ptulsconv.__main__.main()`, 
   which calls :py:func:`ptulsconv.commands.convert()`
#. :func:`ptulsconv.commands.convert()` reads the input with 
   :func:`ptuslconv.docparser.doc_parser_visitor()`,
   which uses the ``parsimonious`` library to parse the input into an abstract
   syntax tree, which the parser visitor uses to convert into a 
   :class:`ptulsconv.docparser.doc_entity.SessionDescriptor`, 
   which structures all of the data in the session output.
#. The next action based on the output format. In the 
   case of the "doc" output format, it runs some validations
   on the input, and calls :func:`ptulsconv.commands.generate_documents()`.
#. :func:`ptulsconv.commands.generate_documents()` creates the output folder, creates the
   Continuity report with :func:`ptulsconv.pdf.continuity.output_continuity()` (this document 
   requires some special-casing), and at the tail calls...
#. :func:`ptulsconv.commands.create_adr_reports()`, which creates folders for 

(FIXME finish this)