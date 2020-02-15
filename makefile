# default command - echos manual for this make file
manual:
	@echo Commands:
	@echo '|-> install = installs python libs from requirements.txt'
	@echo '|-> freeze  = writes all libs to requirements.txt'
	@echo '|-> backup  = create backup of requirements.txt'

# install the requirements file
install: FORCE
	pip3 install -r requirements.txt

# write the requirements file
freeze: FORCE
	pip3 freeze > requirements.txt

# create backup of requirements.txt
backup: FORCE
	cp requirements.txt requirements.backup

# used to ensure that the commands above can always execute
FORCE: