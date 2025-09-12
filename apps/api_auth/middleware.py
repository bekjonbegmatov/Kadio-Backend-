from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from .models import UserModel

from datetime import datetime

class TokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware for user authentication via token.
    Checks for token in Authorization header and adds user to request.
    """
    
    # URLs that don't require authentication
    EXEMPT_URLS = [
        '/api/auth/register/',
        '/api/auth/login/',
        '/admin/',
    ]
    
    def process_request(self, request):
        # Check if URL should bypass authentication
        if self.is_exempt_url(request.path):
            return None
        
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return JsonResponse(
                {'error': 'Access denied. Token not provided.'},
                status=401
            )
        
        # Extract token (expecting "Bearer <token>", "Token <token>" format or just "<token>")
        try:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            elif auth_header.startswith('Token '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
        except IndexError:
            return JsonResponse(
                {'error': 'Invalid token format.'},
                status=401
            )
        
        # Find user by token
        try:
            user = UserModel.objects.get(token=token)
            user.last_active = datetime.now()
            user.save()
            # Add user to request for use in views
            # Store in custom attribute to avoid Django's AuthenticationMiddleware override
            request._authenticated_user = user
            request.user = user
            return None
        except UserModel.DoesNotExist:
            return JsonResponse(
                {'error': 'Access denied. Invalid token.'},
                status=401
            )
    
    def is_exempt_url(self, path):
        """
        Checks if URL should be exempt from authentication.
        """
        for exempt_url in self.EXEMPT_URLS:
            if path.startswith(exempt_url):
                return True
        return False