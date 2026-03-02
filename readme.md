# LegallyDistinctMSPaint

## Links

[Jira](https://chase2450.atlassian.net/jira/software/projects/SCRUM/boards/1)


Provide users with a cross-platform, infinite canvas bitmap editor
People who want an infinite canvas bitmap editor, or infinite canvas doodlers
Do paint stuff

## Functional Requirements

Paint on canvas using brush
Brush can have multiple colors
Infinitely scrollable canvas
Can save to and load from file
Zoom in and out
Erase drawn pixels
RGB color selection
?? Colored pixel counter ??

## Non-functional requirements

Cross-platform
Minimal lag below 10k x 10k canvas size
App should look nice
Non-noticeable latency between drawing action and display on screen
Understandable interface
Navagable entirely by mouse
Navigable entirely by keyboard
	
## Use Case

Actors:
	user/painter
	File system?????
Use cases:
	painting to the canvas
	switching tools
	erasing from the canvas
	Selecting a color
	Save/loading
Boundary:
	no gizmos
	no internet connectivity

## "UML"

Canvas
UI manager
Tool
	Brush
	Eraser
Color Manager
Input Manager
