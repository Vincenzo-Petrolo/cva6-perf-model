from pymtl3 import *

class IssueStage( Component ):
    def construct(s, *args, **kwargs):
        return super().construct(*args, **kwargs)
    
    @update
    def up():
        pass
