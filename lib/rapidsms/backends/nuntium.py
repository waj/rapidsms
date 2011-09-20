from rapidsms.backends.http import RapidHttpBackend
import urllib2
import base64

"""
To use this backend, first create a Nuntium account and application (https://nuntium.instedd.org)
Then append 'nuntium' to the list of available backends:

    "nuntium_backend" : {
        "ENGINE": "rapidsms.backends.nuntium",
        "account": "<my_nuntium_account>",
        "application_name": "<nuntium_application_name>",
        "application_password": "<nuntium_application_password>",
        "server_url": "https://nuntium.instedd.org"     <= Optional, defaults to InSTEDD's server
        "port": 1234        <= Optional, defaults to 8888
    }

"""

class NuntiumBackend(RapidHttpBackend):

    def configure(self, account, application_name, application_password,
                  server_url='https://nuntium.instedd.org', port=8888, **kwargs):
        self.account = account
        self.application_name = application_name
        self.application_password = application_password
        http_args = {
            'port': port,
            'gateway_url': '%(server_url)s/%(account)s/%(application_name)s/send_ao' %
                {
                    'server_url': server_url,
                    'account': account,
                    'application_name': application_name
                },
            'params_outgoing': 'to=%(phone_number)s&body=%(message)s',
            'params_incoming': "from=%(phone_number)s&body=%(message)s"
        }
        self.info(http_args['gateway_url'])
        super(NuntiumBackend, self).configure(**http_args)

    def send(self, message):
        self.info('Sending message: %s' % message)
        context = {'message':urllib2.quote(message.text),
                   'phone_number':message.connection.identity}
        url = "%s?%s" % (self.gateway_url, self.http_params_outgoing % context)
        try:
            self.debug('Sending: %s' % url)
            request = urllib2.Request(url)
            credentials = base64.encodestring('%s/%s:%s' % (self.account, self.application_name, self.application_password))
            auth_header = "Basic %s" % credentials
            request.add_header('Authorization', auth_header)
            response = urllib2.urlopen(request)
        except Exception, e:
            self.exception(e)
            return
        self.info('SENT')
        self.debug(response)