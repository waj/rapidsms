from rapidsms.backends.http import RapidHttpBacked
import urllib2
import base64

class NuntiumBackend(RapidHttpBacked):

    def configure(self, account, application_name, application_password, port=8888, **kwargs):
        self.account = account
        self.application_name = application_name
        self.application_password = application_password
        http_args = {
            'port': port,
            'gateway_url': 'https://nuntium.instedd.org/%(account)s/%(application_name)s/send_ao' %
                {
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