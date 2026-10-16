from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler to standardize API error responses.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'success': False,
            'status_code': response.status_code,
            'message': 'An error occurred while processing your request.',
            'errors': response.data
        }

        # Provide cleaner top-level messages when possible
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_data['message'] = str(response.data['detail'])
            elif response.status_code == 400:
                custom_data['message'] = 'Validation error.'
        elif isinstance(response.data, list):
            custom_data['message'] = response.data[0] if response.data else 'Error'

        response.data = custom_data

    return response
