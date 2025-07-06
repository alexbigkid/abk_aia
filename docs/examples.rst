Examples
========

This page provides comprehensive examples of using the ABK AIA workflow system.

Basic Setup
-----------

.. code-block:: python

   from abk_aia import WorkflowCoordinator, WorkflowConfig, AiaType, WorkflowStatus

   # Configure your GitHub repository
   config = WorkflowConfig(
       repo_owner="your-username",
       repo_name="your-repo",
       project_number=1,  # Your GitHub project number
       default_base_branch="main"
   )

   # Initialize workflow coordinator
   coordinator = WorkflowCoordinator("github", config)

Complete Workflow Example
-------------------------

.. code-block:: python

   # 1. Get issues ready for work
   todo_issues = coordinator.get_todo_issues()
   print(f"Found {len(todo_issues)} issues ready for development")

   # 2. Start ai-coder workflow for an issue
   if todo_issues:
       issue_number = todo_issues[0].number
       result = coordinator.start_coder_workflow(issue_number)
       
       if result.success:
           print(f"✓ Started coder workflow for issue #{issue_number}")
           print(f"Created branch: {result.output}")
       else:
           print(f"✗ Failed to start workflow: {result.message}")

   # 3. Complete coder workflow and move to reviewer
   result = coordinator.complete_coder_workflow(issue_number)
   if result.success:
       print("✓ Moved to review stage, assigned to ai-reviewer")

   # 4. Complete reviewer workflow and move to tester
   result = coordinator.complete_reviewer_workflow(issue_number)  
   if result.success:
       print("✓ Moved to testing stage, assigned to ai-tester")

   # 5. Complete testing and create pull request
   result = coordinator.complete_tester_workflow(
       issue_number=issue_number,
       pr_title=f"Fix: {todo_issues[0].title}",
       pr_body=f"Fixes #{issue_number}\n\nImplemented solution for {todo_issues[0].title}"
   )
   if result.success:
       print("✓ Created pull request, workflow complete")

Research Workflow
-----------------

For issues requiring research before implementation:

.. code-block:: python

   # Assign ai-researcher to an issue
   result = coordinator.assign_researcher_to_issue(issue_number=456)
   if result.success:
       print("✓ Assigned ai-researcher for research phase")

   # After research is complete, remove researcher assignment
   result = coordinator.complete_research_workflow(issue_number=456)
   if result.success:
       print("✓ Research complete, issue ready for development")

   # Now start the normal coder workflow
   result = coordinator.start_coder_workflow(issue_number=456)

Querying Issues by AI Assignment
--------------------------------

.. code-block:: python

   # Get issues assigned to specific AI types
   coder_issues = coordinator.get_issues_for_ai(AiaType.AI_CODER, WorkflowStatus.DOING)
   reviewer_issues = coordinator.get_issues_for_ai(AiaType.AI_REVIEWER, WorkflowStatus.REVIEW)
   tester_issues = coordinator.get_issues_for_ai(AiaType.AI_TESTER, WorkflowStatus.TESTING)

   print(f"AI-Coder has {len(coder_issues)} issues in progress")
   print(f"AI-Reviewer has {len(reviewer_issues)} issues to review")
   print(f"AI-Tester has {len(tester_issues)} issues to test")

Workflow Status Overview
-----------------------

.. code-block:: python

   # Get overview of all issues by status
   status_counts = coordinator.get_workflow_status()
   
   for status, count in status_counts.items():
       print(f"{status.value}: {count} issues")

   # Example output:
   # 📋 ToDo: 5 issues
   # 🔄 Doing: 2 issues  
   # 👀 Review: 1 issues
   # 🧪 Testing: 1 issues
   # ✅ Done: 12 issues

Using Individual Managers
-------------------------

For more granular control, you can work with individual AI managers:

.. code-block:: python

   from abk_aia import AiaManagerFactory, AiaType

   # Create a specific manager
   coder_manager = AiaManagerFactory.create_manager("github", AiaType.AI_CODER, config)

   # Get all issues
   all_issues = coder_manager.get_issues()

   # Get a specific issue
   issue = coder_manager.get_issue(123)

   # Create a branch for an issue
   if issue:
       result = coder_manager.create_branch(issue)
       if result.success:
           print(f"Created branch: {result.output}")

   # Add labels to issues
   result = coder_manager.add_label_to_issue(issue, "priority:high")

   # Assign to AI
   result = coder_manager.assign_to_ai(issue, AiaType.AI_CODER)

Error Handling
--------------

All operations return GitOperation objects with success/failure information:

.. code-block:: python

   result = coordinator.start_coder_workflow(issue_number=999)
   
   if result.success:
       print(f"Success: {result.message}")
       if result.output:
           print(f"Additional info: {result.output}")
   else:
       print(f"Error: {result.message}")
       if result.error:
           print(f"Error details: {result.error}")

Branch Naming Examples
---------------------

The system automatically generates standardized branch names:

.. code-block:: python

   # For a bug issue #123 titled "Fix user login error"
   # Generated branch: B/123/fix-user-login-error

   # For a feature issue #456 titled "Add user profile dashboard"  
   # Generated branch: F/456/add-user-profile-dashboard

   # For a documentation issue #789 titled "Update API documentation"
   # Generated branch: D/789/update-api-documentation

Configuration Examples
---------------------

Different configuration options:

.. code-block:: python

   # Minimal configuration (no project board)
   config = WorkflowConfig(
       repo_owner="username",
       repo_name="repository"
   )

   # Full configuration with project board
   config = WorkflowConfig(
       repo_owner="username", 
       repo_name="repository",
       project_number=1,
       default_base_branch="develop"  # Use develop instead of main
   )

   # Multiple coordinators for different repos
   repo1_coordinator = WorkflowCoordinator("github", config1)
   repo2_coordinator = WorkflowCoordinator("github", config2)