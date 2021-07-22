from rest_framework.throttling import ScopedRateThrottle

EMPLOYEES = ('moderator', 'admin')


class NonEmployeeScopedRateThrottle(ScopedRateThrottle):

    def get_cache_key(self, request, view):
        if request.user.is_authenticated and request.user.role in EMPLOYEES:
            return None

        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
