# coding=utf-8
import httplib2
from datetime import datetime, timedelta, date
from xml.dom.minidom import parseString
import json
from BeautifulSoup import BeautifulSOAP

from WSBilling import F2bCobranca, mensagem, sacador, cobranca, agendamento, sacado


class F2bClient(object):
    __headers = {'content-type': 'text/xml; charset="UTF-8"'}
    __situacao_cobranca = {'url': 'http://www.f2b.com.br/WSBillingStatus',
                           'xsd': 'http://www.f2b.com.br/soap/wsbillingstatus.xsd'}
    __nova_cobranca = {'url': 'http://www.f2b.com.br/WSBilling',
                       'xsd': 'http://www.f2b.com.br/soap/wsbilling.xsd'}

    def __init__(self, conta, senha):
        self.conta = conta
        self.senha = senha

    def nova_cobranca(self, f2bcobranca=None, **kwargs):
        h = httplib2.Http()
        message = self.criar_corpo(f2bcobranca)
        headers = {'SOAPAction': self.__nova_cobranca['url']}
        headers.update(self.__headers)
        response, content = h.request(self.__nova_cobranca['url'], "POST", body=message, headers=headers)
        xml = self.__XmlParser(content)
        if response.status == 200:
            return {'url': xml.parse('url')}
        else:
            return {'log': 'Error - HTTP Code: ' + xml.parse('log')}

    def criar_corpo(self, f2bcobranca=None):
        now = date.today()
        vencimento = now + timedelta(days=2)
        mensagem = ''.join('<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">'
                           '<soap-env:Body>'
                           '<m:F2bCobranca xmlns:m="http://www.f2b.com.br/soap/wsbilling.xsd">'
                           '<mensagem data="' +now.strftime('%Y-%m-%d')+ '" numero="" tipo_ws="' + f2bcobranca.mensagem.tipo_ws + '"/>'
                           '<sacador conta="' + str(f2bcobranca.sacador.conta) + '">' + f2bcobranca.sacador.valueOf_ + '</sacador>'
                           '<cobranca valor="' + str(f2bcobranca.cobranca.valor) +'" tipo_cobranca="'+ f2bcobranca.cobranca.tipo_cobranca +'" num_document="" cod_banco="">'
                           '<demonstrativo>Cobrança F2b</demonstrativo>'
                           '<demonstrativo>Pague em qualquer banco</demonstrativo>'
                           '</cobranca>'
                           '<agendamento vencimento="' + f2bcobranca.agendamento.vencimento.strftime('%Y-%m-%d')+ '" ultimo_dia="" antecedencia="" periodicidade="" periodos="" sem_vencimento="s">Imediato e Agendado</agendamento>'
                           '<sacado>'
                           '<nome>' + f2bcobranca.sacado.nome +'</nome>'
                           '<email>' + f2bcobranca.sacado.email + '</email>'
                           '<cpf>' + str(f2bcobranca.sacado.cpf) +'</cpf>'
                           '</sacado>'
                           '</m:F2bCobranca>'
                           '</soap-env:Body>'
                           '</soap-env:Envelope>')
        return mensagem

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

    wsbilling = F2bCobranca()

    mensagem = mensagem()
    mensagem.data = datetime.now()
    mensagem.numero = ''
    mensagem.tipo_ws = 'WebService'

    wsbilling.mensagem = mensagem

    sacador = sacador()

    sacador.conta = ''
    sacador.valueOf_ = ''

    wsbilling.sacador = sacador

    cobranca = cobranca()

    cobranca.valor = 10
    cobranca.tipo_cobranca = 'B'
    cobranca.num_document = ''
    cobranca.cod_banco = ''

    demonstrativo = ['F2B Cobrança', 'Pague em qualquer banco']
    cobranca.demonstrativo = demonstrativo
    cobranca.sacador_avalista = ''

    wsbilling.cobranca = cobranca

    agendamento = agendamento()
    dias_vencimento = 2
    agendamento.vencimento = date.today() + timedelta(days=dias_vencimento)
    agendamento.valueOf_ = 'Imediato e Agendado'

    wsbilling.agendamento = agendamento

    sacado = sacado()
    sacado.nome = ''
    sacado.email = ''
    sacado.cpf = ''

    wsbilling.sacado = sacado

    f2b = F2bClient('', '')
    retorno = f2b.nova_cobranca(wsbilling)
    print json.dumps(retorno, indent=4)
