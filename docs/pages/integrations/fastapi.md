If you don't read the [setup instruction](./setup.md), please do so first.

=== "Depends"
    ```python
    import re
    from typing import Annotated
    from fastapi import FastAPI, APIRouter, Depends, Header
    from doti18n import LocaleData
    
    app = FastAPI()
    router = APIRouter()
    i18n = LocaleData("locales")
    pattern = re.compile(r"[a-z]{2}")
    
    async def get_language_code(accept_language: str = Header(alias="Accept-Language")) -> str:
        if not accept_language:
            return i18n.default_locale
        
        for match in re.finditer(pattern, accept_language):
            language_code = match.group()
            if language_code in i18n.loaded_locales:
                return language_code
        
        return i18n.default_locale
    
    @router.get("/")
    async def main(language_code: Annotated[str, Depends(get_language_code)]):
        t = i18n[language_code].main
        
        return {"message": t.hello}
    
    app.include_router(router)

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="localhost", port=8000)
    ```

=== "Middleware"
    ```python
    import re
    from typing import Optional
    from fastapi import FastAPI, Request, APIRouter
    from starlette.middleware.base import BaseHTTPMiddleware
    from doti18n import LocaleData
    
    app = FastAPI()
    i18n = LocaleData("locales")
    router = APIRouter()
    pattern = re.compile(r"[a-z]{2}")
    
    class I18nMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            accept_language = request.headers.get('accept-language')
            language = self._get_best_match_language(accept_language)
            request.state.locale = language
            request.state.translator = i18n[language]
            response = await call_next(request)
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
    
    @router.get("/")
    async def main(request: Request):
        t = request.state.translator
        
        return {"message": t.hello}
    
    
    app.add_middleware(I18nMiddleware)
    app.include_router(router)
    
    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="localhost", port=8000)
    ```


!!! warning
    **Don't use** that method of language detection in production as it is quite basic.
    That's only for **demonstration** purposes.
