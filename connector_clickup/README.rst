*********************
**Connector Clickup**
*********************

**Description**
***************

* The Connector Clickup module allows you to integrate ClickUp, a project management tool, with your application. This module provides various functionalities to import and export projects and tasks between your application and ClickUp's remote website. By using the Connector Clickup module, you can efficiently manage project data and synchronize it with ClickUp.

**Author**
**********

* This module is developed by BizzAppDev Systems Pvt. Ltd.

**Configuration**
*****************


**To set up the Connector Clickup module, you need to provide the following information:**


* API Key: An API token obtained from ClickUp to authenticate your application's access to ClickUp's API.
* Location/URI: The unique identifier known as the space id is required from where you want to import or export projects and tasks.


**Features & Highlights**
*************************


**The Connector Clickup module offers the following functionalities:**

**Import Projects and Tasks:**

* Import projects and their corresponding tasks from ClickUp into your application.
* Use the provided API token and Space ID to specify the source in ClickUp.
* Retrieve project data such as project name, description, start and end dates and other relevant information.
* Retrieve task data such as task name, description, deadline, tags and other relevant information.
* Map imported projects to the corresponding entities in your application.
* If the last task update time is same as the time stored in project.task level then it will save extra processing time in queue job to import that task.

**Export Projects and Tasks:**

* Export projects and their tasks from your application to ClickUp's remote website.
* We can set space ID in project level to specify the destination in ClickUp else it will be exported in default backend's space id.
* Transfer project data, including project name, description, task details, and any associated metadata.
* Ensure synchronization between your application and ClickUp by exporting changes made in your application.

**Batch Processing:**

* Through One click we can get all projects available to that space and same applies to stages and tasks.
* Perform bulk imports or exports by utilizing queue jobs with user friendly description.
* Use related button in queue job to redirect to project, stage or task record.
* Queue jobs enable you to process multiple projects or tasks simultaneously, improving efficiency.
* Track the status of queued operations and handle any errors or mapping issues.

**Task-Level Operations:**

* Import Changes in individual tasks from ClickUp website by clicking the "Update To Clickup" button in the task form view.
* Export Changes from individual tasks To ClickUp Website by clicking the "Update To Clickup" button in the task form view.
* Particular task can be open in clickup website by clicking "Open Task In Clickup" button in task form view.

**Project-Level Operations:**

* Update a project and its tasks From ClickUp Website by clicking the "Update From Clickup" button in the project form view.
* Update a project and its tasks to Clickup Wbsite by clicking the "Update To Clickup" button in project form view.
* Export a particular project and its tasks to ClickUp by clicking the "Export To Clickup" button in the project form view.
* By clicking on boolean field and selecting the folder id in project form view we can export project to that particular folder in clickup website.
* Retrieve project-specific information and manage synchronization between your application and ClickUp.
* Particular project can be open in clickup website by clicking "Open Project In Clickup" button in Project form view.

**Multi-Company Functionality:**

* We can select any particular company and then can import project and tasks for that company specifically.

**Automation:**

* Using the scheduled action we can import the project,stage,task or export the project,task of all the clickup backend record automatically.

**Access Rights:**

* As a connector manager you can access all the features and functionality.
* As a user only that access rights are available which are provided by Odoo itself.

**Current Behaviour/Future Scope**
**********************************

* Currently only That stages can be imported that is implemented for folder level or whole space level in clickup website.
* Currently we need to provide the team id in backend that helps to open particular project at clickup website.
* Currently if we dont choose folder to export particular project,by default it will be exported in to the space.
* Currently We need to first create stage in clickup website, import that stage in order to use that stage in tasks.
* Currently If the Stage already exist in project.task.type model the queue job will raise mapping error for that particular record.
* Currently If the stages are not imported before importing the tasks it can cause queue job fail as the stages not found for tasks.
* Currently importing tasks directly can import it's projects first but the performance of it is unstable.
* Implementation of Oauth 2.0.

**Changelog**
*************

* No changelog information is available for this module at the moment.
