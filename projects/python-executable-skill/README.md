# Python Backend Executable Builder (Claude Skill)

## Overview
This project demonstrates a **Claude Skill** that helps developers convert a Python backend application into a **Windows executable (.exe)** using PyInstaller.

The skill automates the process of building, packaging, and preparing a Python application for release.

## How to Create the Skill

1. Open Claude and ask to create new skill
2. Add a description(prompt) explaining how the skill should be.
3. Provide instructions for building the skill.

## Prompt used to generate the skill

    Create a skill that automates building a Python backend executable using the PyInstaller library.
    The skill should follow these steps:
    1. Use the existing `.spec` file present in the provided project folder to build the executable with PyInstaller.
    2. After the executable is successfully created, copy all files and folders from the `dist` folder to the root `api` folder.
    3. Create a new folder named `python_backend_exe` in the same directory as the project.
    4. Copy the following files and folders into the `python_backend_exe` folder:
    * `_internal` folder
    * Generated `.exe` file
    * `server.spec` file
    * ask to provide the required filenames or filepaths and copy them into new folder
    5. Ensure the final folder (`python_backend_exe`) contains everything required to run the backend executable independently.
    The skill should also:
    * Validate that the `.spec` file exists before starting the build.
    * Handle errors if the build fails.
    * Log each step of the process.
    * ask user to provide the required filenames or filepaths and copy them into new folder as well


## Ways to use the skill

1. Claude Code (best for local projects) - Install Claude Code on your machine. Then the skill runs locally with full access to your file system
2. Run the script - Download the "build_backend_exe.py" script from the skill and run it manually in your terminal

## What the Skill Helps With

The skill guides the user through:

- preparing the Python project
- running PyInstaller
- generating the `.exe` file
- organizing the release output
- versioning the build

---

## Screenshots

Screenshots in the `screenshots` folder show:

- skill creation process
- prompt configuration
- Claude processing the request
- generated build instructions

---

## Purpose

This project demonstrates how **Claude Skills can automate repetitive developer workflows**, such as packaging and releasing Python backend applications.