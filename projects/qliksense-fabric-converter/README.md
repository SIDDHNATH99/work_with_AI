# Qlik Sense → Microsoft Fabric Conversion Tool (Claude Project)

## Overview
This project explores how **Claude AI** can assist in converting **Qlik Sense data transformation scripts** into a **Microsoft Fabric–compatible architecture and implementation plan**.

Using **Claude Projects**, a Qlik Sense script is analyzed and transformed into a structured migration document that includes Fabric architecture design, SQL transformations, pipelines, and semantic model setup.

## Benefits of Using Claude Projects
Claude Projects provide several advantages when working with complex workflows:

- Can be used individually or shared with teams
- Supports attaching files and folders for context
- Allows adding system instructions to guide AI behavior
- Maintains project-level context across prompts

## What the Tool Generates
The output is delivered as a **single Microsoft Fabric–ready `.txt` document** containing structured sections such as:

- Architecture breakdown
- Source mapping
- Fabric **Bronze, Silver, and Gold** layer design
- Data warehouse table definitions
- Spark SQL transformations
- Pipeline execution steps
- Semantic model configuration
- Migration deployment plan
- Risk assessment and mitigation

## Prompts
Deliver full migration of this attached qliksense script into microsoft fabric friendly txt file and output should be in one single txt file

## Claude Feature Used

**Claude Projects**
The project maintains context across prompts and generates a structured migration blueprint for the Fabric platform.

## Purpose
This experiment demonstrates how AI can assist with **data platform migration planning**, reducing manual effort when translating legacy Qlik Sense scripts into modern lakehouse architectures.

## Status
Built while learning Claude AI.