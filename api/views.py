import requests
import json
from django.conf import settings as st
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from liveagent.logger import logger
from api.models import LineSession
from django.views.generic import View
from django.http import JsonResponse
from liveagent.process import process_message


class SetupView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def get_liveagent_session(line_id):
    session_obj = LineSession.get_by_line(line_id=line_id)
    if session_obj is None:
        url = st.LIVEAGENT_HOST + '/chat/rest/System/SessionId'
        headers = {
            'X-LIVEAGENT-API-VERSION': st.API_VERSION,
            'X-LIVEAGENT-AFFINITY': 'null',
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            res_data = json.loads(r.text)
            res_data.update({
                'line_id': line_id,
                'sequence': 1,
            })
            try:
                return LineSession.save_session(res_data)
            except:
                pass

    return session_obj


def init_liveagent(line_id, display_name=None, prechat_entities=None):
    if display_name is None:
        return
    session = get_liveagent_session(line_id)
    url = st.LIVEAGENT_HOST + '/chat/rest/Chasitor/ChasitorInit'
    headers = {
        'X-LIVEAGENT-API-VERSION': st.API_VERSION,
        'X-LIVEAGENT-AFFINITY': session.get('affinity_token'),
        'X-LIVEAGENT-SESSION-KEY': session.get('key'),
        'X-LIVEAGENT-SEQUENCE': str(session.get('sequence')),
    }
    post_data = {
        'organizationId': st.LIVEAGENT_ORGANIZATION_ID,
        'deploymentId': st.LIVEAGENT_DEPLOYMENT_ID,
        'buttonId': st.LIVEAGENT_BUTTON_ID,
        'sessionId': session.get('liveagent_id'),
        'userAgent': st.USER_AGENT,
        'language': 'ja',
        'trackingId': '',
        'screenResolution': '',
        'visitorName': display_name,
        'isPost': True,
        'receiveQueueUpdates': True,
        'buttonOverrides': [],
        'prechatDetails': [
            {
                'label': 'ContactLineId',
                'value': session.get('line_id'),
                'entityMaps': [],
                'transcriptFields': [],
                'displayToAgent': True,
                'doKnowledgeSearch': False
            },
        ],
    }
    post_data.update({'prechatEntities': prechat_entities})

    r = requests.post(url, json=post_data, headers=headers)
    if r.status_code == 200:
        LineSession.update_session({
            'line_id': line_id,
            'sequence': str(session.get('sequence') + 1),
        })
        return True
    else:
        LineSession.delete_session(line_id)
        return False


class LiveagentInit(SetupView):
    @staticmethod
    def post(request):
        result = None
        status = 200
        res_type = None
        received_data = json.loads(request.body)
        line_id = received_data.get('line_id')
        display_name = received_data.get('display_name')
        prechat_entities = received_data.get('prechatEntities')

        is_valid = init_liveagent(line_id, display_name, prechat_entities)
        if is_valid is True:
            res_type, result = connect_liveagent(line_id)
        else:
            LineSession.delete_session(line_id)

        return JsonResponse({
            'type': res_type,
            'message': result
        }, status=status)


def connect_liveagent(line_id):
    session = LineSession.get_by_line(line_id=line_id)
    if session is None:
        session = get_liveagent_session(line_id)

    url = st.LIVEAGENT_HOST + '/chat/rest/System/Messages'
    headers = {
        'X-LIVEAGENT-API-VERSION': st.API_VERSION,
        'X-LIVEAGENT-AFFINITY': session.get('affinity_token'),
        'X-LIVEAGENT-SESSION-KEY': session.get('key'),
    }
    r = requests.get(url, headers=headers, params={
        'ack': session.get('ack', -1)
    })
    try:
        result = None
        res_type = None
        if r.status_code == 200:
            body = json.loads(r.text)
            for message in body.get('messages'):
                res_type, result = process_message(message)

            if res_type == 'end' or res_type == 'fail':
                LineSession.delete_session(line_id)
            else:
                LineSession.update_session({
                    'line_id': line_id,
                    'ack': body.get('sequence'),
                })

        elif r.status_code == 204:
            LineSession.delete_session(line_id)

        return [res_type, result]

    except Exception as ex:
        logger.info(ex)
        return ['error', ex]


def get_message_liveagent(line_id):
    session = LineSession.get_by_line(line_id=line_id)
    if session is None:
        return ['bad', 'bad request']

    url = st.LIVEAGENT_HOST + '/chat/rest/System/Messages'
    headers = {
        'X-LIVEAGENT-API-VERSION': st.API_VERSION,
        'X-LIVEAGENT-AFFINITY': session.get('affinity_token'),
        'X-LIVEAGENT-SESSION-KEY': session.get('key'),
    }
    r = requests.get(url, headers=headers, params={
        'ack': session.get('ack', -1)
    })
    try:
        res_type = None
        result = None
        if r.status_code == 200:
            body = json.loads(r.text)
            for message in body.get('messages'):
                res_type, result = process_message(message)

            if res_type == 'end' or res_type == 'fail':
                LineSession.delete_session(line_id)
            else:
                LineSession.update_session({
                    'line_id': line_id,
                    'ack': body.get('sequence'),
                })

            return [res_type, result]

        elif r.status_code == 204:
            get_message_liveagent(line_id)

    except Exception as ex:
        logger.info(ex)
        return ['error', ex]


class LiveagentMessages(SetupView):
    @staticmethod
    def post(request):
        received_data = json.loads(request.body)
        line_id = received_data.get('line_id')
        res_type, result = get_message_liveagent(line_id)
        return JsonResponse({
            'type': res_type,
            'message': result
        }, status=200)


class LiveagentClose(SetupView):
    @staticmethod
    def post(request):
        received_data = json.loads(request.body)
        line_id = received_data.get('line_id')
        LineSession.delete_session(line_id)
        return JsonResponse({
            'type': 'end',
            'message': 'deleted session'
        }, status=200)


class LiveagentSend(SetupView):
    @staticmethod
    def post(request):
        received_data = json.loads(request.body)
        line_id = received_data.get('line_id')
        message = received_data.get('message')
        session = LineSession.get_by_line(line_id=line_id)
        if session is None:
            return JsonResponse({
                'type': 'bad',
                'message': 'bad request'
            }, status=400)
        url = st.LIVEAGENT_HOST + '/chat/rest/Chasitor/ChatMessage'
        headers = {
            'X-LIVEAGENT-API-VERSION': st.API_VERSION,
            'X-LIVEAGENT-AFFINITY': session.get('affinity_token'),
            'X-LIVEAGENT-SESSION-KEY': session.get('key'),
            'X-LIVEAGENT-SEQUENCE': str(session.get('sequence')),
        }
        post_data = {
            'text': message
        }
        r = requests.post(url, json=post_data, headers=headers)
        if r.status_code == 200:
            LineSession.update_session({
                'line_id': line_id,
                'sequence': session.get('sequence') + 1,
            })
            return JsonResponse({
                'type': 'send',
                'message': 'send'
            }, status=200)
        else:
            LineSession.delete_session(line_id)
            return JsonResponse({
                'type': 'bad',
                'message': 'bad request'
            }, status=400)
