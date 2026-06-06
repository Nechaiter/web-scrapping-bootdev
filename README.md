
# Init
UV is a package manager like pip
`uv init <Proyect name>` creates a basic template with git
`uv vent` create a virtual enviroment (We want this to download package only inside of the proyecy/enviroment)
`source .venv/bin/activate` activates the enviroment
`.venv\Scripts\activate.bat` cmd
# Packages
`uv pip list` to check current packages
`uv add <pagacke name>` to add a package 

# TDD 
Use `uv run -m unittest` to run a test or `uv run -m unittest discover ./tests/`

