start-kafka:
	docker-compose up --scale tremor=0 --scale elastic=0 -V

stop-all:
	docker-compose down

start-tremor:
	docker-compose scale tremor=1
stop-tremor:
	docker-compose scale tremor=0

restart-tremor: stop-tremor start-tremor

start-elastic:
	docker-compose scale elastic=1

stop-elastic:
	docker-compose scale elastic=0

.PHONY: start-kafka stop-all start-tremor stop-tremor restart-tremor start-elastic stop-elastic