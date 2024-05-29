from pymtl3 import *

class IssueStage(Component):
    def construct(s):
        s.fetch_valid_i = InPort()
        s.fetch_ready_o = OutPort()
        # Define other inputs and outputs as needed
        s.issue_valid_o = OutPort()

        @update
        def issue_logic():
            # Implement issue stage logic here
            s.fetch_ready_o @= 0
            s.issue_valid_o @= s.issue_valid_o
            pass

class ExecutionStage(Component):
    def construct(s):
        s.issue_valid_i = InPort()
        s.issue_ready_o = OutPort()
        # Define other inputs and outputs as needed

        @update
        def execution_logic():
            # Implement execution stage logic here
            s.issue_ready_o @= not s.issue_ready_o
            pass

class CommitStage(Component):
    def construct(s):
        s.issue_valid_o = OutPort()
        s.issue_ready_i = InPort()
        # Define other inputs and outputs as needed

        @update
        def commit_logic():
            # Implement commit stage logic here
            s.issue_valid_o @= not s.issue_valid_o
            pass

class Backend(Component):
    def construct(s):
        s.issue_stage = IssueStage()
        s.execution_stage = ExecutionStage()
        s.commit_stage = CommitStage()

        # Connect stages together
        connect(s.issue_stage.issue_valid_o, s.execution_stage.issue_valid_i)
        connect(s.execution_stage.issue_ready_o, s.commit_stage.issue_ready_i)

        # Define clock and reset
        s.clk_i = InPort()
        s.rst_ni = InPort()
    
        @update
        def prova():
            pass

