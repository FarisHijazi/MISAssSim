# Project Proposal COE403 M-Architecture Emulator - term 182

## Table of Contents

- [Project Proposal COE403 M-Architecture Emulator - term 182](#project-proposal-coe403-m-architecture-emulator---term-182)
  - [Table of Contents](#table-of-contents)
  - [Team members](#team-members)
  - [Instructor requirements](#instructor-requirements)
  - [Project description](#project-description)
    - [Proposed solution](#proposed-solution)
  - [Tools](#tools)
    - [Simulators (that might be useful)](#simulators-that-might-be-useful)
  - [Project execution plan](#project-execution-plan)

## Team members

| Name            | ID         |
| --------------- | ---------- |
| Faris Hijazi    | s201578750 |
| Taha Alsadah    | s201434020 |
| Rakan Aalsoraye | s201238740 |

******

## Instructor requirements

- Identify clearly the **problem** that will be addressed in your project.
- Identify clearly the **tools** that will be used in your project.
- Identify the **outcome** of your project (a software simulator, a hardware prototype, etc.)
- Provide an **execution plan** for the project tasks and the time duration of each task.
- **Final document** and outcome is due on **Saturday, April 13**.
- **Project presentation** will be on **Sunday, April 14** during class time.

## Project description

Our goal is to create a functional emulator for the [M architecture]().  
The minimum requirement is to have the assembler working, and to have a functional simulator (to execute instructions).

### Proposed solution

## Tools

We may be using already existing open source emulators and modify them to support the m-architecture.  

### Simulators (that might be useful)

- [MARS](https://github.com/thomasrussellmurphy/MARS_Assembler) ([docs here](http://courses.missouristate.edu/KenVollmar/MARS/Help/MarsHelpIntro.html))
- [Legv8-emulator](https://github.com/c4wrd/legv8-emulator)
- [unicorn engine](http://www.unicorn-engine.org/) ([github repo](https://github.com/unicorn-engine/unicorn)) lightweight multi-platform, multi-architecture CPU emulator framework
- [Visual ARM emulator](https://bitbucket.org/salmanarif/visual-release/src)  
  VisUAL makes use of the following third-party tools & libraries:
  - [RSyntaxTextArea](http://bobbylight.github.io/RSyntaxTextArea/) Copyright © 2012, Robert Futrell.
  - [NSMenuFX](https://github.com/codecentric/NSMenuFX) Copyright © 2015, codecentric AG.
  - [ControlsFX](http://fxexperience.com/controlsfx/) Copyright © 2013, ControlsFX.
  - [Apache Commons I/O](https://commons.apache.org/proper/commons-io/) Copyright © 2002-2014, The Apache Software Foundation.
  - [Oracle Java SE](http://www.oracle.com/technetwork/java/javase/overview/index.html) Copyright © Oracle Corporation.

Tools and libraries:

- [Pydgin](https://github.com/cornell-brg/pydgin)
  A (Py)thon (D)SL for (G)enerating (In)struction set simulators.

## Project execution plan

| Tasks                          | Estimated time |
| ------------------------------ | -------------- |
| Research and finalize tools    | 1 week         |
| Reading and understanding code | 2 week         |
| Writing code and testing       | 2 weeks        |