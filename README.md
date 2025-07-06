# AWS Billing Reminder System

This project implements an automated AWS billing reminder system using AWS EventBridge, Lambda, and SNS.

## Architecture

- AWS EventBridge triggers the Lambda function daily at 22:00 PM UTC
- Lambda function fetches billing information using AWS Cost Explorer API
- AWS SNS sends the billing information via email to subscribed users

## Features

- Daily billing alerts
- Cost breakdown by service
- Month-to-date total cost
- Serverless architecture
- Easy deployment using custom python script