SAS App Engine Smartform
========================

Overview
--------
Smartform is a library for abstracting the solicitation of user input in a
generic and flexible way. A server can produce an XML document describing a
number of fields with constraints and pass it by API to a client. The client
can then present the form to the user in a manner native to its platform. For
example, a browser or mobile app would present a graphical form, while a
command-line client could interactively present questions. The client then
collects the responses into another XML document and presents it to the server.
