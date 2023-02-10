build:
	docker build -t my-python-sandbox:v1 .

test: build
ifeq ("$(JIRA_PW)","")
	@echo "ERROR: Environment variables JIRA_USER and JIRA_PW, required and at least one is not defined.  Please define/export and try again."
else
	docker run -e JIRA_USER=$(JIRA_USER) -e JIRA_PW=$(JIRA_PW) -v <TODO update path>files:/workspace -it --rm my-python-sandbox:v1
endif

run: build
ifeq ("$(JIRA_PW)","")
	@echo "ERROR: Environment variables JIRA_USER and JIRA_PW, required and at least one is not defined.  Please define/export and try again."
else
	docker run -e JIRA_USER=$(JIRA_USER) -e JIRA_PW=$(JIRA_PW) -v <TODO update path>files:/workspace -it --rm my-python-sandbox:v1
endif