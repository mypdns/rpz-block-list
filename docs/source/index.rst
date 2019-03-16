Start
=====

Welcome to www.mypdns.org
=========================

You have probably been wondering why we are hiding who own's our domains used to run and maintain the RPZ zones.

The reason is actually rather simple, and yet very very sad, and the very reason why this project have been born.

The free and open DNS service is violating laws in many countries like ex. Denmark, which actually isn't a democratic country.... there are lot's of censuring going on and laws that says you have to block access to 10000's of domains if you have a open DNS server.
Some of these domain are applied by law other by companies like Sony and interest organizations.

Another reason we are here is because it's bad for the free democracy that commercial companies and governments tracking all of you're activities on all kind of devices with internet access, YES even your TV and Radio collect data about you.

Our domains:
^^^^^^^^^^^^
- matrix.rocks
- mypdns.cloud
- mypdns.com
- mypdns.org

A simple whois mypdns.cloud you'll get:
```
Domain Name: mypdns.cloud
Registry Domain ID: D92572D3CC69F46EC9EE510B585D4B0A5-NSR
Registrar WHOIS Server: whois.namesilo.com
Registrar URL: www.namesilo.com
Updated Date: 2019-01-03T02:09:55Z
Creation Date: 2018-10-04T18:33:11Z
Registry Expiry Date: 2028-10-04T18:33:11Z
Registrar: NameSilo, LLC
Registrar IANA ID: 1479
Registrar Abuse Contact Email:
Registrar Abuse Contact Phone:
Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
```

The WHOIS
^^^^^^^^^

```
Domain Name: mypdns.cloud
Registry Domain ID: D92572D3CC69F46EC9EE510B585D4B0A5-NSR
Registrar WHOIS Server: whois.namesilo.com
Registrar URL: www.namesilo.com
Updated Date: 2019-01-03T02:09:55Z
Creation Date: 2018-10-04T18:33:11Z
Registry Expiry Date: 2028-10-04T18:33:11Z
Registrar: NameSilo, LLC
Registrar IANA ID: 1479
Registrar Abuse Contact Email: https://www.mypdns.org/trac/newticket?summary=Please%20write%20%20short%20subject&reporter=your@email.tld&owner=admin&milestone=0&verion=0&priority=minor&component=contact&type=task&severity=mild&description=Long%20description%20of%20your%20question
Registrar Abuse Contact Phone: https://www.mypdns.org/trac/newticket?summary=Please%20write%20%20short%20subject&reporter=your@email.tld&owner=admin&milestone=0&verion=0&priority=minor&component=contact&type=task&severity=mild&description=Long%20description%20of%20your%20question
Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
Registry Registrant ID:
Registrant Name: My Private DNS
Registrant Organization: My Private DNS
Registrant Street:
Registrant Street:
Registrant Street:
Registrant City:
Registrant State/Province: N/A
Registrant Postal Code:
Registrant Country: N/A
Registrant Phone:
Registrant Phone Ext:
Registrant Fax:
Registrant Fax Ext:
Registrant Email: https://www.mypdns.org/trac/newticket?summary=Please%20write%20%20short%20subject&reporter=your@email.tld&owner=admin&milestone=0&verion=0&priority=minor&component=contact&type=task&severity=mild&description=Long%20description%20of%20your%20question
```

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


