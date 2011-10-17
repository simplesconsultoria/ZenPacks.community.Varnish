# ZenPacks.community.Varnish
This ZenPack adds a template to Zenoss to monitor a Varnish server.

## HowTo
In order to use this package you need **first ** setup a cronjob in the target 
machine to export the results of varnishstat:

    */2 * * * *	/<path_to_varnish>/bin/varnishstat -1 > /var/www/status/varnish.txt

The above example will generate a varnish.txt file containing the stats every 
2 minutes. 

This file must be accessible through the web in order to our pack access it.