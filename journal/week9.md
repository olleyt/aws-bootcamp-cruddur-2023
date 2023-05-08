# Week 9 — CI/CD with CodePipeline, CodeBuild and CodeDeploy

## CodePipeline - Initial Setup

Firstly we will need to setup CodePipeline in AWS console.
Navigate to CodePipeline and click on create button.

### Source Stage
We will need to connect the pipeline to our GitHub repo and will use GitHub version 2 connection with OAuth.
Connect to Github, click on create connection, then install GitHub application and authorize AWS CodeBuild to cruddur repo:
![CB_Oauth](../_docs/assets/week-9/CodeBuild_Github_Oauth.png)

Then go to GitHub and create a new branch prod from main. We will use this prod branch to trigger CodePipeline when code changes from main are merged to prod branch.

Now we are ready to create connection to the repository from the CodePipeline:
![CP_source_phase](../_docs/assets/week-9/CodePipeline_source_phase.png)

### Build Stage
Skip build stage for now, we will come back to this stage when CodeBuild setup is completed.

### Deploy Stage

This stage cannot be skipped. 
Create a stage and then create action inside of this stage
Choose ECS as action provider and fill other parameters like on the sreenshot below:
![CP_deploy_def1](../_docs/assets/week-9/CodePipeline_deploy_phase.png)

Try to run the pipeline, the run will fail, and it is expected because of invalid configuration:
![CP_deploy_run1](../_docs/assets/week-9/CodePipeline_first_run_failed.png)

At this stage, our pipeline is configured like this:
![CP_2_stages](../_docs/assets/week-9/CodePipeline_source_deploy_stages_only.png)

## Create CodeBuild project

Set up the CodeBuild as on the screenshots below:
![CB_1](../_docs/assets/week-9/CodeBuild_project_configuration.png)
![CB_2](../_docs/assets/week-9/CodeBuild_source.png)
![CB_3](../_docs/assets/week-9/CodeBuild_Env_priviledge_checked.png)

Change timeout to 15 mins but keep VPC clear
![CB_4](../_docs/assets/week-9/CodeBuild_timeout_noVpc.png)
![CB_5](../_docs/assets/week-9/CodeBuild_hooks_events.png)
![CB_6](../_docs/assets/week-9/CodeBuild_Artifacts_Logs.png)

Copy the buildspec.yml from Andrew's repo and commit it to your Cruddur repo, we will need to refer it in the CodeBuild like so:
![CB_7](../_docs/assets/week-9/CodeBuild_buildspec.png)

Note: there is probably wild card for origin on backend-flask container and we need to address this vulnerability soon

Add badge image to your [README.md](../README.md) file in the Cruddur repo in main branch and commit it.
Create a pull request and merge this change from main to prod branch. This shall trigger CodePipeline.

However, the build failed because CodeBuild needed access to ECR. I added an IAM policy 'cruddur-ecr-dev-policy' to the CodeBuild role and next build succeded. The badge on [README.md](../README.md) shall reflect that. How cool is that?!
![Readme_tag](../_docs/assets/week-9/Readme_added_tag_CodeBuild.png)

### Adding Build Stage to CodePipeline

Go back to the CodePipile, edit the cruddur backend-flask pipeline, add build stage that I called 'bake'.
Put 'ImageDefinitions' as output artifacts.
Change input on deploy phase as 'ImageDefinitions'

If we go to ECS, no tasks are running becuase of desired capacity was set to 0 to save on cost. We need to update this to 1.
Don't forget to update MyIP on the ALB security group inbound rules.
Check that ALB target groups return healthy and cruddur ```/api/health-check``` returns
```json
{
    success: True
}
```
![ALB_old_health_check](../_docs/assets/week-9/ALB_old_health_check_true.png)

Now we can do a minor check in app.py on the health-check route to evidence that CodePipeline deploys changes.
Open a pull request and merge this code change to to prod. CodePipeline shall be triggered:
![CP_triggered](../_docs/assets/week-9/CodePipeline_triggered_health-check.jpg)

Go to ECS and evidence that new task was created:
 ![ECS_new](../_docs/assets/week-9/ECS_created_new_task.png)

 Check ALB is created a new task:
 ![ALB_new_task](../_docs/assets/week-9/ALB_registered_new_task.png)
 and the old one was draining:
 ![ALB_old_task_draining](../_docs/assets/week-9/ALB_draining_old_task.png)

After new task is fully created, check that the CodePipeline succeeded:
![CP_success](../_docs/assets/week-9/CodePipeline_first_success.png)

Evidence that new health-check returned on ```/api/health-check```:
![new_health_check](../_docs/assets/week-9/updated_health_check.png)

This proves that the CodePipeline successfully deployed code changes.