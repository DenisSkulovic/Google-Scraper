from scraper_logging import create_logger


class ExceptionHandler(object):
    LOGGER = create_logger()
    
    def __init__(self, error, raise_error=False, info={}):
        self.error = error
        self.raise_error = raise_error
        self.info = info

    def __call__(self, function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except:
                message = f"EXCEPTION in: {function.__name__}\nERROR: {self.error}"
                for key, value in self.info.items():
                    message += f'\n{key}: {value}'                   
                self.LOGGER.debug(message)
                if self.raise_error == True:
                    raise self.error
        return wrapper
    
    
class ScraperException(Exception):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)    
                
class BrowserStartException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class ClickException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class TextSubmissionException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class BrowseToPageException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
                
class InfoCollectionException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
                
class DateLinkCollectionException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class DateRangeGenerationException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class ResultsPageCollectionException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)   

class KeysInputException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        
class SubmissionException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        
class GetElementException(ScraperException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 