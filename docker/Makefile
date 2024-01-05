
# generate the temporary build tag
BUILD_TIME_TAG := make-build-$(shell od -An -N3 -i /dev/random | tr -d ' ')

sinclude Makefile.custom

BUILD_DIR := $(PWD)
# use all files named Dockerfile under the docker directory
DOCKERFILES := $(shell find * -type f -name Dockerfile)

# check forbidden chains in branch name, commit history and files content
RESULT_CHAINS = $(foreach CHAIN,$(FORBIDDEN_CHAINS),$(shell ((git rev-parse --abbrev-ref HEAD | grep -i $(CHAIN) --quiet) || (grep -ir $(CHAIN) .. --quiet) || (git log --pretty=%B | grep -i $(CHAIN) --quiet)) && echo forbidden || echo allowed))
IS_FORBIDDEN := $(shell ((echo $(RESULT_CHAINS) | grep forbidden --quiet) && echo true || echo false))

# check whether tree is clean - only then proper tags are created
$(shell git diff --exit-code --quiet)
GIT_IS_CLEAN := $(shell git diff --exit-code --quiet && echo clean || echo dirty)

GIT_COMMIT_TAG := $(if $(filter $(GIT_IS_CLEAN),clean),commit-$(shell git rev-parse HEAD),)
GIT_BRANCH_TAG := $(if $(filter $(GIT_IS_CLEAN),clean),branch-$(shell git rev-parse --abbrev-ref HEAD | tr / -),)
GIT_TAG_TAGS := $(if $(filter $(GIT_IS_CLEAN),clean),$(foreach tag,$(shell git tag --points-at HEAD),tag-$(tag)),)

IMAGES := $(subst /,\:,$(subst /Dockerfile,,$(DOCKERFILES)))
BUILD_IMAGES := $(foreach image,$(IMAGES),build-$(image))
PUSH_IMAGES := $(filter-out push-base, $(filter-out %-builder, $(foreach image,$(IMAGES),push-$(image))))
HISTORY_IMAGES := $(foreach image,$(IMAGES),history-$(image))
RUN_IMAGES := $(foreach image,$(IMAGES),run-$(image))
CLEAN_IMAGES := $(foreach image,$(IMAGES),clean-$(image))

# summarize all tags to be used for images - local-build is always assigned but not pushed
PUBLIC_TAGS := $(GIT_COMMIT_TAG) $(GIT_BRANCH_TAG) $(GIT_TAG_TAGS)
PRIVATE_TAGS := local-build
ALL_TAGS := $(PUBLIC_TAGS) $(PRIVATE_TAGS)

DEPENDS := .depends.mk

# TODO FROM other other repositories should not be handled by automatic resolution
#
.PHONY: all explain build push show-git-commit-tag show-git-tag-tag show-git-branch-tag show-git-is-clean show-tags $(BUILD_IMAGES) $(PUSH_IMAGES) $(HISTORY_IMAGES) $(RUN_IMAGES) $(CLEAN_IMAGES)

.DEFAULT_GOAL := build

# by default, only build
all: build

build: $(BUILD_IMAGES)
check-forbidden-chains:
	@echo "Forbidden chains: $(FORBIDDEN_CHAINS)"
ifeq ($(if $(FORBIDDEN_CHAINS),true,false),true)
ifeq ($(IS_FORBIDDEN),true)
	$(error "ONE OF FORBIDDEN CHAIN DETECTED ($(FORBIDDEN_CHAINS)). FAILING...")
endif
endif
	@echo "No forbidden chain detected."

push: $(PUSH_IMAGES)
clean: $(CLEAN_IMAGES)

show-git-is-clean:
	@echo $(GIT_IS_CLEAN)

show-git-commit-tag:
	@echo $(GIT_COMMIT_TAG)

show-git-branch-tag:
	@echo $(GIT_BRANCH_TAG)

show-git-tag-tags:
	@echo $(GIT_TAG_TAGS)

show-tags:
	@echo $(ALL_TAGS)


explain:
	@echo $(BUILD_TIME_TAG)
	@echo $(DOCKERFILES)
	@echo $(IMAGES)
	@echo $(BUILD_IMAGES)
	@echo $(PUSH_IMAGES)
	@echo $(HISTORY_IMAGES)


# create file with dependencies of push-some-image on build-some-image
$(DEPENDS): $(DOCKERFILES) Makefile
	@for image in $(IMAGES) ; do echo push-$$image: build-$$image ; echo history-$$image: build-$$image ; done > $@

# and now use this dependencies file
sinclude $(DEPENDS)

# setup default values for IMAGE variable
$(BUILD_IMAGES): IMAGE?=$(subst build-,,$@)
$(PUSH_IMAGES): IMAGE?=$(subst push-,,$@)
$(HISTORY_IMAGES): IMAGE?=$(subst history-,,$@)
$(RUN_IMAGES): IMAGE?=$(subst run-,,$@)
$(CLEAN_IMAGES): IMAGE?=$(subst clean-,,$@)

# setup default values for CONTEXT_PATH and DOCKERFILE_PATH - they may be overridden in Makefile.custom
$(BUILD_IMAGES): CONTEXT_PATH?=$(subst :,/,$(IMAGE))
$(BUILD_IMAGES): DOCKERFILE_PATH?=$(BUILD_DIR)/$(IMAGE)/Dockerfile

$(PUSH_IMAGES) $(BUILD_IMAGES) $(HISTORY_IMAGES) $(RUN_IMAGES) $(CLEAN_IMAGES): FULL_IMAGE_NAME=$(REGISTRY_DOMAIN)/$(REGISTRY_PROJECT)/${REGISTRY_APPLICATION}/$(IMAGE)

# the actual recipe for all build-some-image targets
# first run docker build with proper context path and dockerfile path and place it under a temporary tag BUILD_TIME_TAG
# then for each tag in TAGS tag this newly created image, like some-image:branch-develop, some-image:commit-abc123, etc.
# finally remove the temporary tag
$(BUILD_IMAGES):
	docker build \
		$(if $(or $(NO_IMAGE_PULL), $(BUILDER_IMAGE), $(BASE_IMAGE)),, --pull) \
		$(if $(shell grep 'ARG BASE_IMAGE' $(DOCKERFILE_PATH)), --build-arg BASE_IMAGE=$(BASE_IMAGE),) \
		$(if $(shell grep 'ARG BUILDER_IMAGE' $(DOCKERFILE_PATH)), --build-arg BUILDER_IMAGE=$(BUILDER_IMAGE),) \
		-t $(FULL_IMAGE_NAME):$(BUILD_TIME_TAG) $(CONTEXT_PATH) -f $(DOCKERFILE_PATH)
	$(foreach tag,$(ALL_TAGS),docker tag $(FULL_IMAGE_NAME):$(BUILD_TIME_TAG) $(FULL_IMAGE_NAME):$(tag);)

$(CLEAN_IMAGES):
	@docker image rm $(FULL_IMAGE_NAME):$(BUILD_TIME_TAG) || true > /dev/null

# for all tags registered push all images
$(PUSH_IMAGES):
	$(foreach tag,$(PUBLIC_TAGS),docker push $(FULL_IMAGE_NAME):$(tag);)

$(HISTORY_IMAGES):
	docker history $(FULL_IMAGE_NAME):local-build

$(RUN_IMAGES):
	docker run -ti --rm --name $(IMAGE) $(FULL_IMAGE_NAME):local-build bash
