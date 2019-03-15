Start
=====


Hopefully some usefull documentation for our RPZ zones and howto's

Quiclist:
^^^^^^^^^

.. code-block:: python


	.rpz-passthru (Trigger PASSTHRU Action)
	.rpz-drop (Drop Containing (IP))
	google.com CNAME . (return NXDOMAIN for google.com)
	*.google.com CNAME . (return NXDOMAIN for all subdomains in google.com)
	24.0.0.0.127.rpz-client-ip CNAME rpz-drop (Drop all requests from clients in network 127.0.0.1/24)
	.32.2.3.4.10.rpz-ip CNAME . (NXDOMAIN)
	*.google.com.rpz-nsdname (NXDOMAIN all responses that comes from dns server with name *.google.com)


