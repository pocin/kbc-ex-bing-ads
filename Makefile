IMAGE=pocin/kbc-ex-bing-ads
VERSION=v0.1.0
BASECOMMAND=docker run -it --rm -v `pwd`:/src -e KBC_DATADIR='/data/' pocin/kbc-ex-bing-ads:latest

build-dev:
	docker build . -t $(IMAGE):dev

build:
	docker build . -t $(IMAGE):$(VERSION) -t $(IMAGE):latest

test:
	$(BASECOMMAND) ./run_tests.sh

sh:
	$(BASECOMMAND) /bin/ash

run:
	$(BASECOMMAND)

deploy:
	echo "Pushing to dockerhub"
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest
