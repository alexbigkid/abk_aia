Git AI Assistant Manager
=======================

.. automodule:: abk_aia.git_aia_manager
   :members:
   :undoc-members:
   :show-inheritance:

The git_aia_manager module provides the core functionality for managing AI assistant workflows across different Git providers.

Base Classes
------------

.. autoclass:: abk_aia.git_aia_manager.AiaManagerBase
   :members:
   :undoc-members:
   :show-inheritance:

Provider Implementations
-----------------------

GitHub Manager
~~~~~~~~~~~~~~

.. autoclass:: abk_aia.git_aia_manager.GitHubAiaManager
   :members:
   :undoc-members:
   :show-inheritance:

GitLab Manager
~~~~~~~~~~~~~~

.. autoclass:: abk_aia.git_aia_manager.GitLabAiaManager
   :members:
   :undoc-members:
   :show-inheritance:

Bitbucket Manager
~~~~~~~~~~~~~~~~~

.. autoclass:: abk_aia.git_aia_manager.BitbucketAiaManager
   :members:
   :undoc-members:
   :show-inheritance:

Factory
-------

.. autoclass:: abk_aia.git_aia_manager.AiaManagerFactory
   :members:
   :undoc-members:
   :show-inheritance:

Enumerations
------------

Branch Types
~~~~~~~~~~~~

.. autoclass:: abk_aia.git_aia_manager.GitBranchType
   :members:
   :undoc-members:
   :show-inheritance:

AI Assistant Types
~~~~~~~~~~~~~~~~~~

.. autoclass:: abk_aia.git_aia_manager.AiaType
   :members:
   :undoc-members:
   :show-inheritance:

Branch Naming Convention
------------------------

The system uses standardized branch naming:

- **B**: Bug fix branches
- **D**: Documentation branches
- **F**: Feature branches
- **R**: Research branches
- **T**: Test branches

Format: `{prefix}/{issue_number}/{short_name}`

Example: `F/123/add-user-authentication`
