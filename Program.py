# coding=utf-8
import httplib2
from datetime import datetime
from xml.dom.minidom import parseString
import json


class F2bClient(object):
    """
    A Cobrança F2b é um conjunto de serviços, disponíveis para os usuários de contas no sistema F2b,
    que permitem o registro e envio de cobranças por e-mail e impresso por correio, além da administração
    do recebimento e pagamento destas cobranças.
    Estes serviços estão disponíveis no site da F2b (www.f2b.com.br) para seus usuários ao acessar as
    contas.
    """
    __headers = {'content-type': 'text/xml; charset="UTF-8"'}
    __situacao_cobranca = {'url': 'http://www.f2b.com.br/WSBillingStatus',
                           'xsd': 'http://www.f2b.com.br/soap/wsbillingstatus.xsd'}
    __nova_cobranca = {'url': 'http://www.f2b.com.br/WSBilling',
                       'xsd': 'http://www.f2b.com.br/soap/wsbilling.xsd'}

    def __init__(self, conta, senha):
        '''
        conta = O número do cartão da conta F2b do sacador. Ex: “9023010001230123”
        senha = Chave definida para acesso via WebService 
        '''
        self.conta = conta
        self.senha = senha

    def situacao_cobranca(self, **kwargs):
        h = httplib2.Http()
        query = self.__create_query(cobranca=kwargs)
        soap = self.__soap_message(self.__situacao_cobranca['xsd'], 'F2bSituacaoCobranca', query)
        headers = {'SOAPAction': self.__situacao_cobranca['url']}
        headers.update(self.__headers)
        response, content = h.request(self.__situacao_cobranca['url'], "POST", body=soap, headers=headers)
        xml = self.__XmlParser(content)
        if response.status == 200:
            return {'cliente': xml.parse('cliente'), 'cobrancas': xml.parse('cobranca'), 'total': xml.parse('total'),
                    'log': xml.parse('log')}
        else:
            return {'log': 'Error - HTTP Code: ' + response.status}

    def __create_query(self, **kwargs):
        now = datetime.now()
        query_parts = ['<mensagem data="', now.strftime('%Y-%m-%d'), '" numero="', str(int(now.strftime('%H%M%S%f'))),
                       '"/>''<cliente conta="', str(self.conta), '" senha="', str(self.senha), '"/><cobranca numero="" situacao="0" />']
        for key, val in kwargs.iteritems():
            if type(val) == dict:
                query_parts.append('<' + key)
                for attr, attr_val in val.iteritems():
                    query_parts.append(' ' + attr + '="' + str(attr_val) + '"')
                query_parts.append(' />')
                pass
            else:
                query_parts.append('<' + key + '>' + val + '</' + key + '>')
        return ''.join(query_parts)

    def __soap_message(self, xsd, action, body):
        message = ''.join(
            ['<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsb="', xsd,
             '">''<soapenv:Header/>''<soapenv:Body>''<wsb:',
             action, '>', body, '</wsb:', action, '>''</soapenv:Body>''</soapenv:Envelope>'])
        return message

    class __XmlParser(object):
        '''
        XML Parsing Helper
        '''

        def __init__(self, xml_string):
            '''
            Construtor
            '''
            self.dom = parseString(xml_string)

        def parse(self, root_node):
            '''
            Transforma os nodes XML em um dict decente
            '''
            nodes = self.dom.getElementsByTagName(root_node)

            if len(nodes) == 0:
                return None

            first_node = nodes[0].firstChild
            if first_node != None and first_node.nodeName == '#text':
                return first_node.data

            results = []
            for node in nodes:
                result = {}
                for attr in node.attributes.keys():
                    result[attr] = node.attributes[attr].value
                for child in node.childNodes:
                    result[child.nodeName] = child.firstChild.data
                results.append(result)
            return results




if __name__ == '__main__':
    f2b = F2bClient('', '')
    registros = f2b.situacao_cobranca(situacao=0, registro='2011-09-01', registro_final='2011-10-28')
    print json.dumps(registros, indent=4)
