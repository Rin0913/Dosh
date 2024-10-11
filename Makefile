.PHONY: test lint init init-k8s init-ca init-config

lint:
	pylint ./

test:
	pytest ./

init-k8s:
	kubectl apply -f ./k8s_yaml/dosh-namespace.yaml
	kubectl create -f ./k8s_yaml/kyverno.yaml
	kubectl apply -f ./k8s_yaml/limit-deployment-policy.yaml
	kubectl apply -f ./k8s_yaml/unauthorized-access-policy.yaml

init-ca:
	openssl genrsa -out ./data/ca/private.key 2048
	openssl req -x509 -new -nodes -key ./data/ca/private.key -sha256 -days 3650 -out ./data/ca/certificate.crt -subj "/CN=dosh.sandb0x.tw"

init-config:
	cp ./config.py.sample ./config.py

init: init-k8s init-ca init-config
