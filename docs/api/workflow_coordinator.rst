Workflow Coordinator
===================

.. automodule:: abk_aia.workflow_coordinator
   :members:
   :undoc-members:
   :show-inheritance:

The WorkflowCoordinator class manages the complete AI assistant workflow from issue assignment through code implementation, review, testing, and pull request creation.

Key Methods
-----------

.. autoclass:: abk_aia.workflow_coordinator.WorkflowCoordinator
   :members:
   :undoc-members:
   :show-inheritance:

Workflow Transitions
--------------------

The coordinator manages these workflow state transitions:

1. **ToDo → Doing**: `start_coder_workflow()`
2. **Doing → Review**: `complete_coder_workflow()`  
3. **Review → Testing**: `complete_reviewer_workflow()`
4. **Testing → Done**: `complete_tester_workflow()`

AI Assistant Types
------------------

- **ai-coder**: Implements code solutions
- **ai-reviewer**: Performs code reviews
- **ai-tester**: Creates and executes tests
- **ai-researcher**: Conducts research and analysis
- **ai-marketeer**: Handles marketing and documentation