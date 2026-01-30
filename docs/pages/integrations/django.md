If you don't read the [setup instruction](./setup.md), please do so first.

=== "Middleware (Recommended)"
    **`middleware.py`**
    ```python
    import re
    from typing import Optional
    from doti18n import LocaleData
    
    # Initialize your locales (supports JSON, YAML, XML)
    i18n = LocaleData("locales")
    pattern = re.compile(r"[a-z]{2}")
    
    class I18nMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response
    
        def __call__(self, request):
            accept_language = request.headers.get('Accept-Language')
            language = self._get_best_match_language(accept_language)
            request.locale = language
            request.t = i18n[language]
            response = self.get_response(request)
            return response
    
        @staticmethod
        def _get_best_match_language(accept_language: Optional[str]) -> str:
            if not accept_language:
                return i18n.default_locale
            
            for match in re.finditer(pattern, accept_language):
                language_code = match.group()
                if language_code in i18n.loaded_locales:
                    return language_code
            
            return i18n.default_locale
    ```

    **`settings.py`**
    ```python
    MIDDLEWARE = [
        # ... other middleware ...
        'path.to.your.middleware.I18nMiddleware',
    ]
    ```

    **`views.py`**
    ```python
    from django.http import JsonResponse
    
    def main(request):
        t = request.t.main
        
        return JsonResponse({"message": t.hello})
    ```

=== "View Utility"
    ```python
    import re
    from django.http import JsonResponse, HttpRequest
    from django.urls import path
    from doti18n import LocaleData
    
    i18n = LocaleData("locales")
    pattern = re.compile(r"[a-z]{2}")
    
    def get_language_code(request: HttpRequest) -> str:
        """
        Parses the Accept-Language header and returns the best matching locale code.
        """
        accept_language = request.headers.get("Accept-Language", "")
        
        if not accept_language:
            return i18n.default_locale
        
        for match in re.finditer(pattern, accept_language):
            language_code = match.group()
            if language_code in i18n.loaded_locales:
                return language_code
        
        return i18n.default_locale
    
    def main(request: HttpRequest):
        language_code = get_language_code(request)
        t = i18n[language_code].main
        
        return JsonResponse({"message": t.hello})

    urlpatterns = [
        path('', main),
    ]
    ```

!!! warning
    **Don't use** that method of language detection in production as it is quite basic.
    That's only for **demonstration** purposes.