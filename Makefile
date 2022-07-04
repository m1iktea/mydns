image_name ?= mydns

.PHONY: build
build:
	docker build -t mi1ktea/tools:$(image_name) .

.PHONY: push
push:
	docker push mi1ktea/tools:$(image_name)

.PHONY: clean
clean:
	docker system prune -a -f --volumes

all: build push
