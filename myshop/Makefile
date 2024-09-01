CREDENTIALS=oauth.env

.PHONY: run-service
run-service:
	@set -a && source ${CREDENTIALS} && set +a && \
	if uname | grep -q 'Darwin'; then \
	  . ~/.local/pipx/venvs/django/bin/activate && \
	  python3 manage.py migrate > /dev/null && \
	  python3 manage.py runserver > /dev/null; \
	else \
	  python manage.py migrate > /dev/null && \
	  python manage.py runserver > /dev/null; \
	fi

.PHONY: install-dependencies
install-dependencies:
	- pip install django > /dev/null
	- pip install django-admin > /dev/null
	- pip install django-allauth > /dev/null
	- pip install Pillow > /dev/null
	- pip install jwt > /dev/null
	- pip install requests > /dev/null