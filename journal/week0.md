# Week 0 — Billing and Architecture

## Introduction
This week will reflect on:
* understanding Cruddr investors needs, 
* what do they want to build
* what are the technical and budget constraints 
* contextual and logical design for the app
* setting up AWS account, users and groups, OUs,and access outside of AWS for GitPod environments.
* as there is a budget constraint to keep the budget to minimum and as a best practice, AWS budgets and CloudWatch alarms need to be created to track spending

## Initial design

It was important to understand what Cruddr is envisioned to be and what constraints are in place before choosing specific AWS services. 
For example, budget constraint to keep cost near $0 impacts how computing layer will be designed as not all AWS services such as Fargate have free tier.



### Contextual Diagram
As a solutions architect, I sketched a conceptual diagram on the napkin during first meeting with Cruddr investors (all right, it was part of the Week 0 lesson video).
![Cruddur Contextual Diagram](../_docs/assets/E733D494-DA56-4EDA-8087-629EB3AC56EB.jpeg)

Ouch; as I progressed through the video, I've learned that napkin design shall not include specific services / technologies mentioned yet. That shall be depicted on a logical architecture diagram.

This is another version of the conceptual diagram on a napkin in a more abstracted way: 
![Cruddur Abstracted Contextual Diagram](../_docs/assets/A6EA9421-267A-41D1-BC50-562207923CD8.jpeg)
## CI/CD Pipeline
This is the starting point for CI/CD pipeline as I see it for the Cruddur application

![Cruddur CI/CD pipeline](../_docs/assets/DevSecOpsPipline.png)

I also depicted a more detailed CI/CD pipeline inspired by 'Be a better Dev' YouTube video 'Ideal Pipeline':
![Cruddur Advanced CI/CD pipeline](../_docs/assets/26720410-B3A6-4E5D-927E-B917419452D5.jpeg)
