# DocItUp

A simple Dokumentation Generator based on Markdown. It's a python script so you have to have python 2.6 or greater installed. a simple style.css is included feel free to restyle it. DocItUp relies on highlight.js for syntax highlighting.

# usage

Just Edit the settings.json file like so

	{
		"project_name" : "MY PROJECT",
		"build_path" : "YOUR BUILD PATH",
		"hooks" : [["git", "add", "."],["git", "commit", "-am", "DocItUp"],["git", "push"]]
	}

You can also pass a list of command to execute after  the build is finished in the hooks attribute


