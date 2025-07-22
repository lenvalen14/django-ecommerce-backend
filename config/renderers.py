from rest_framework.renderers import JSONRenderer

class CustomResponseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_status = renderer_context['response'].status_code
        message = data.pop('message', '')

        if isinstance(data, dict) and {'results', 'count', 'next', 'previous'}.issubset(data.keys()):
            data = {
                'items': data['results'],
                'meta': {
                    'count': data['count'],
                    'next': data['next'],
                    'previous': data['previous']
                }
            }

        response = {
            'message': message or self._default_message(response_status),
            'code': response_status,
            'data': data
        }

        return super().render(response)

    def _default_message(self, status_code):
        if 200 <= status_code < 300:
            return 'Success'
        if 400 <= status_code < 500:
            return 'Client Error'
        if 500 <= status_code:
            return 'Server Error'
        return ''
