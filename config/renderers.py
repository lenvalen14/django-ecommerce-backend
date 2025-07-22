from rest_framework.renderers import JSONRenderer

class CustomResponseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_status = renderer_context['response'].status_code
        message = ''
        response_data = None
        meta = None

        if isinstance(data, dict):
            message = data.pop('message', '')

            # Nếu là dạng pagination
            if {'results', 'count', 'next', 'previous'}.issubset(data.keys()):
                response_data = data['results']
                meta = {
                    'count': data['count'],
                    'next': data['next'],
                    'previous': data['previous']
                }
            else:
                response_data = data or None

        # Base response
        response = {
            'message': message or self._default_message(response_status),
            'code': response_status
        }

        # Thêm data nếu có
        if response_data is not None:
            response['data'] = response_data

        # Thêm meta nếu có
        if meta is not None:
            response['meta'] = meta

        return super().render(response, accepted_media_type, renderer_context)

    def _default_message(self, status_code):
        if 200 <= status_code < 300:
            return 'Success'
        elif 400 <= status_code < 500:
            return 'Client Error'
        elif 500 <= status_code:
            return 'Server Error'
        return ''
