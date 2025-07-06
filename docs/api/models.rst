Data Models
===========

.. automodule:: abk_aia.models
   :members:
   :undoc-members:
   :show-inheritance:

The models module defines data structures for issues, pull requests, workflow configuration, and Git operations used throughout the AI assistant workflow system.

Issue Management
----------------

.. autoclass:: abk_aia.models.Issue
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: abk_aia.models.IssueState
   :members:
   :undoc-members:
   :show-inheritance:

Pull Request Management
-----------------------

.. autoclass:: abk_aia.models.PullRequest
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: abk_aia.models.PullRequestState
   :members:
   :undoc-members:
   :show-inheritance:

Workflow Configuration
----------------------

.. autoclass:: abk_aia.models.WorkflowConfig
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: abk_aia.models.WorkflowStatus
   :members:
   :undoc-members:
   :show-inheritance:

Git Operations
--------------

.. autoclass:: abk_aia.models.GitOperation
   :members:
   :undoc-members:
   :show-inheritance:

Workflow States
---------------

The system defines these kanban workflow states:

- **📋 ToDo**: Issues ready to be started
- **🔄 Doing**: Issues currently being worked on  
- **👀 Review**: Issues under code review
- **🧪 Testing**: Issues being tested
- **✅ Done**: Completed issues with PRs created