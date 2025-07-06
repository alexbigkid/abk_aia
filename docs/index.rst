ABK AIA Documentation
=====================

Welcome to the AI Assistant Git Workflow Interface documentation.

.. image:: https://img.shields.io/badge/python-3.13+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :alt: License

ABK AIA provides a standardized interface for AI assistant collaboration with Git repositories. It supports structured workflows and multi-provider Git integration.

Features
--------

✨ **Multi-provider support** - GitHub, GitLab, Bitbucket

🏷️ **Standardized branch naming** - [B|D|F|R|T] + / + issue number + / + short name

🤖 **AI assistant coordination** - ai-coder, ai-reviewer, ai-tester, ai-researcher, ai-marketeer

📋 **Automated kanban workflow** - ToDo → Doing → Review → Testing → Done

🔗 **GitHub project integration** - Seamless project board management

📝 **Issue and pull request management** - Complete workflow automation

Quick Start
-----------

.. code-block:: python

   from abk_aia import WorkflowCoordinator, WorkflowConfig

   # Configure your repository
   config = WorkflowConfig(
       repo_owner="your-username",
       repo_name="your-repo", 
       project_number=1
   )

   # Initialize workflow coordinator
   coordinator = WorkflowCoordinator("github", config)

   # Start ai-coder workflow for issue #123
   result = coordinator.start_coder_workflow(123)
   if result.success:
       print(f"Branch created: {result.output}")

Installation
------------

Install using uv (recommended):

.. code-block:: bash

   uv add abk-aia

Or using pip:

.. code-block:: bash

   pip install abk-aia

Requirements
~~~~~~~~~~~~

- Python 3.13+
- GitHub CLI (gh) for GitHub operations
- Git for local operations

API Reference
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/modules
   api/workflow_coordinator
   api/git_aia_manager  
   api/models
   examples
   changelog

Core Components
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/
   :template: module.rst

   abk_aia.workflow_coordinator
   abk_aia.git_aia_manager
   abk_aia.models

Workflow Examples
-----------------

**Starting a coder workflow:**

.. code-block:: python

   # Move issue from ToDo to Doing, assign to ai-coder, create branch
   result = coordinator.start_coder_workflow(issue_number=123)

**Completing coder workflow:**

.. code-block:: python

   # Move to Review, assign to ai-reviewer  
   result = coordinator.complete_coder_workflow(issue_number=123)

**Creating a pull request:**

.. code-block:: python

   # Complete testing and create PR
   result = coordinator.complete_tester_workflow(
       issue_number=123,
       pr_title="Fix: User authentication issue",
       pr_body="Fixes #123\n\nImplements secure authentication flow"
   )

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`