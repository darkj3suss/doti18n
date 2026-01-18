If you don't read the [setup instruction](./setup.md), please do so first.

=== "Helper Function"
    ```python
    import re
    from flask import Flask, request
    from doti18n import LocaleData
    
    app = Flask(__name__)
    i18n = LocaleData("locales")
    pattern = re.compile(r"[a-z]{2}")
    
    def get_language_code() -> str:
        accept_language = request.headers.get("Accept-Language")
        
        if not accept_language:
            return i18n.default_locale
        
        for match in re.finditer(pattern, accept_language):
            language_code = match.group()
            if language_code in i18n.loaded_locales:
                return language_code
        
        return i18n.default_locale
    
    @app.route("/")
    def main():
        language_code = get_language_code()
        t = i18n[language_code].main
        
        return {"message": t.hello}
    
    if __name__ == "__main__":
        app.run(host="localhost", port=8000)
    ```

=== "Middleware"
    ```python
    import re
    from typing import Optional
    from flask import Flask, request, g
    from doti18n import LocaleData
    
    app = Flask(__name__)
    i18n = LocaleData("locales")
    pattern = re.compile(r"[a-z]{2}")
    
    def _get_best_match_language(accept_language: Optional[str]) -> str:
        if not accept_language:
            return i18n.default_locale
        
        for match in re.finditer(pattern, accept_language):
            language_code = match.group()
            if language_code in i18n.loaded_locales:
                return language_code
        
        return i18n.default_locale
    
    @app.before_request
    def detect_language():
        accept_language = request.headers.get('Accept-Language')
        language = _get_best_match_language(accept_language)

        g.locale = language
        g.t = i18n[language]
    
    @app.route("/")
    def main():
        t = g.t.main
        
        return {"message": t.hello}
    
    if __name__ == "__main__":
        app.run(host="localhost", port=8000)
    ```


!!! warning
    **Don't use** that method of language detection in production as it is quite basic.
    That's only for **demonstration** purposes.